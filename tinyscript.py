import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from optimizer import Optimizer
from errors import TinyScriptRuntimeError

UPDATE_STATE_FILE = ".tinyscript_update_state.json"
DEFAULT_UPDATE_SERVER = "https://tinyscript-update-worker.altholder06.workers.dev"


def _script_root():
    return Path(__file__).resolve().parent


def _state_path():
    return _script_root() / UPDATE_STATE_FILE


def _load_update_state():
    state_file = _state_path()
    if not state_file.exists():
        return {}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_update_state(state):
    state_file = _state_path()
    try:
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _fetch_update_info(update_server, channel):
    url = f"{update_server.rstrip('/')}/update?channel={channel}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "TinyScript-Updater",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
            message = detail.get("message", str(exc))
        except (json.JSONDecodeError, OSError, AttributeError):
            message = str(exc)
        raise RuntimeError(f"Update server returned {exc.code}: {message}") from exc

    required_fields = ("version", "url", "sha256")
    missing = [f for f in required_fields if f not in payload]
    if missing:
        raise RuntimeError(f"Update server response is missing fields: {missing}")

    # Validate server-supplied fields before trusting them
    version = str(payload["version"])
    url = str(payload["url"])
    sha256 = str(payload["sha256"])
    if not re.fullmatch(r"[0-9a-fA-F]{64}", sha256):
        raise RuntimeError("Update server response has a malformed sha256 (expected 64 hex chars)")
    if url and not urllib.parse.urlparse(url).scheme == "https":
        raise RuntimeError("Update server supplied a non-HTTPS download URL")

    return payload


def _download_file(url, target_path, max_bytes=256 * 1024 * 1024):
    # Security: only allow https download sources
    if not url.lower().startswith("https://"):
        raise urllib.error.URLError(f"Refusing non-HTTPS download URL: {url!r}")
    req = urllib.request.Request(url, headers={"User-Agent": "TinyScript-Updater"})
    downloaded = 0
    with urllib.request.urlopen(req, timeout=60) as response:
        # Defense against oversized/hostile payloads exhausting disk or memory
        length = response.headers.get("Content-Length")
        if length and length.isdigit() and int(length) > max_bytes:
            raise urllib.error.URLError(
                f"Download too large ({length} bytes > {max_bytes} limit)"
            )
        with open(target_path, "wb") as out_file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > max_bytes:
                    raise urllib.error.URLError(
                        f"Download exceeded size limit ({max_bytes} bytes)"
                    )
                out_file.write(chunk)


def _sha256_of_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _should_skip_path(rel_path):
    parts = rel_path.parts
    if not parts:
        return True
    banned = {".git", "__pycache__", ".venv", "venv"}
    return any(part in banned for part in parts)


def _safe_extract(zip_file, target_dir):
    target_dir = target_dir.resolve()
    for member in zip_file.infolist():
        member_path = (target_dir / member.filename).resolve()
        if member_path != target_dir and target_dir not in member_path.parents:
            raise ValueError(f"Refusing to extract unsafe path outside target directory: {member.filename!r}")
    zip_file.extractall(target_dir)


def apply_update_from_worker(update_server, channel, force=False):
    state = _load_update_state()
    state_key = f"{update_server}@{channel}"
    local_version = state.get(state_key)

    try:
        info = _fetch_update_info(update_server, channel)
    except (urllib.error.URLError, RuntimeError) as exc:
        print(f"Update check failed: {exc}", file=sys.stderr)
        return False
    except json.JSONDecodeError as exc:
        print(f"Update check failed: update server response is not valid JSON ({exc})", file=sys.stderr)
        return False

    remote_version = info["version"]
    download_url = info["url"]
    expected_sha256 = info["sha256"].lower()
    mandatory = bool(info.get("mandatory", False))

    if not force and local_version == remote_version:
        print(f"Already up to date at {remote_version} (channel: {channel}).")
        return True

    if info.get("notes"):
        print(f"Release notes for {remote_version}: {info['notes']}")
    if mandatory:
        print("This update is marked as mandatory by the server.")

    root = _script_root()
    with tempfile.TemporaryDirectory(prefix="tinyscript-update-") as tmpdir:
        zip_path = Path(tmpdir) / "update.zip"
        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            _download_file(download_url, zip_path)
        except urllib.error.URLError as exc:
            print(f"Download failed: {exc}", file=sys.stderr)
            return False

        actual_sha256 = _sha256_of_file(zip_path)
        if actual_sha256 != expected_sha256:
            print(
                f"Update aborted: SHA-256 mismatch (expected {expected_sha256}, got {actual_sha256}). "
                "The downloaded file may be corrupted or tampered with.",
                file=sys.stderr,
            )
            return False

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                _safe_extract(zf, extract_dir)
        except (OSError, zipfile.BadZipFile, ValueError) as exc:
            print(f"Update extraction failed: {exc}", file=sys.stderr)
            return False

        extracted_roots = [p for p in extract_dir.iterdir() if p.is_dir()]
        if len(extracted_roots) == 1 and not any(p.is_file() for p in extract_dir.iterdir()):
            repo_root = extracted_roots[0]
        else:
            repo_root = extract_dir

        updated_count = 0
        added_count = 0
        for src in repo_root.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(repo_root)
            if _should_skip_path(rel):
                continue
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            existed = dest.exists()
            shutil.copy2(src, dest)
            if existed:
                updated_count += 1
            else:
                added_count += 1

    state[state_key] = remote_version
    _save_update_state(state)
    print(
        f"Update applied: channel '{channel}' -> {remote_version}. "
        f"Updated {updated_count} file(s), added {added_count} file(s)."
    )
    return True


class TinyScript:
    def __init__(self, optimize=True):
        self.optimize_enabled = optimize
        self.interpreter = Interpreter()
        self.optimizer = Optimizer()

    def compile_and_run(self, source_code, show_tokens=False, show_ast=False, capture_output=False):
        try:
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()

            if show_tokens:
                print("=" * 60)
                print("TOKENS:")
                print("=" * 60)
                for token in tokens:
                    if token.type.name != 'NEWLINE' and token.type.name != 'EOF':
                        print(f"  {token}")
                print()

            parser = Parser(tokens)
            ast = parser.parse()

            if show_ast:
                print("=" * 60)
                print("ABSTRACT SYNTAX TREE:")
                print("=" * 60)
                self._print_ast(ast, indent=0)
                print()

            if self.optimize_enabled:
                ast = self.optimizer.optimize(ast)
                if show_ast:
                    print("=" * 60)
                    print("OPTIMIZED AST:")
                    print("=" * 60)
                    self._print_ast(ast, indent=0)
                    print()

            if capture_output:
                buf = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = buf
                try:
                    self.interpreter.run(ast)
                finally:
                    sys.stdout = old_stdout
                print("=" * 60)
                print("OUTPUT:")
                print("=" * 60)
                emitted = buf.getvalue()
                if emitted:
                    print(emitted, end='')
            else:
                print("=" * 60)
                print("OUTPUT:")
                print("=" * 60)
                self.interpreter.run(ast)
            return True

        except SyntaxError as e:
            print(f"Syntax error: {e}", file=sys.stderr)
            return False
        except TinyScriptRuntimeError as e:
            print(f"Runtime error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return False

    def _print_ast(self, node, indent=0):
        from parser import BlockNode

        prefix = "  " * indent

        if isinstance(node, BlockNode):
            print(f"{prefix}Block:")
            for stmt in node.statements:
                self._print_ast(stmt, indent + 1)
        else:
            print(f"{prefix}{node}")

    def run_file(self, filename, show_tokens=False, show_ast=False):
        try:
            with open(filename, 'r', encoding='utf-8', errors='strict') as f:
                source_code = f.read()

            print(f"Running {filename}...")
            print()
            return self.compile_and_run(
                source_code,
                show_tokens,
                show_ast,
                capture_output=True,
            )

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.", file=sys.stderr)
            return False
        except OSError as exc:
            print(f"Error reading file '{filename}': {exc}", file=sys.stderr)
            return False

    def repl(self):
        print("=" * 60)
        print("TinyScript REPL (Read-Eval-Print Loop)")
        print("Type 'exit' or 'quit' to exit")
        print("=" * 60)
        print()

        while True:
            try:
                line = input(">>> ")

                if line.strip() in ('exit', 'quit'):
                    print("Goodbye!")
                    break

                if not line.strip():
                    continue

                self.compile_and_run(line)
                print()

            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    argp = argparse.ArgumentParser(description='TinyScript Compiler/Interpreter')
    argp.add_argument('file', nargs='?', help='TinyScript file to run')
    argp.add_argument('--no-optimize', action='store_true', help='Disable optimization')
    argp.add_argument('--show-tokens', action='store_true', help='Show tokens')
    argp.add_argument('--show-ast', action='store_true', help='Show AST')
    argp.add_argument('--repl', action='store_true', help='Start interactive REPL')
    argp.add_argument('--self-update', action='store_true', help='Check the update server and apply a newer version if available')
    argp.add_argument('--auto-update', action='store_true', help='Check/update before running file or REPL')
    argp.add_argument('--force-update', action='store_true', help='Apply the update even if the local version already matches')
    argp.add_argument('--update-url', default=DEFAULT_UPDATE_SERVER, help='Base URL of the update Worker')
    argp.add_argument('--update-channel', default='stable', choices=['stable', 'beta', 'nightly'], help='Update channel')

    args = argp.parse_args()

    if args.self_update or args.auto_update:
        ok = apply_update_from_worker(
            update_server=args.update_url,
            channel=args.update_channel,
            force=args.force_update,
        )
        if not ok:
            sys.exit(1)
        if args.self_update and not args.file and not args.repl:
            sys.exit(0)

    compiler = TinyScript(optimize=not args.no_optimize)

    if args.repl or not args.file:
        compiler.repl()
        sys.exit(0)

    sys.exit(0 if compiler.run_file(args.file, args.show_tokens, args.show_ast) else 1)


if __name__ == '__main__':
    main()
