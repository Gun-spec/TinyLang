"""
TinyScript Compiler and Interpreter
Main entry point for the language
"""

import argparse
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from optimizer import Optimizer
from errors import TinyScriptRuntimeError

UPDATE_STATE_FILE = ".tinyscript_update_state.json"


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
        # Non-fatal: updater still succeeded even if state cannot be written.
        pass


def _fetch_latest_commit_sha(repo, branch):
    url = f"https://api.github.com/repos/{repo}/commits/{branch}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "TinyScript-Updater",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["sha"]


def _download_zipball(repo, branch, target_zip_path):
    url = f"https://api.github.com/repos/{repo}/zipball/{branch}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "TinyScript-Updater",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        with open(target_zip_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)


def _should_skip_path(rel_path):
    parts = rel_path.parts
    if not parts:
        return True
    banned = {".git", "__pycache__", ".venv", "venv"}
    return any(part in banned for part in parts)


def _safe_extract(zip_file, target_dir):
    """
    Extract a zip file, refusing any entry that would land outside target_dir.
    A crafted archive can name entries like "../../etc/passwd" or use an
    absolute path, and a plain extractall() will happily write there. Since
    this zip comes from the network, we can't fully trust its contents even
    when it's fetched over HTTPS from the expected repo, so every member's
    resolved path is checked before anything touches disk.
    """
    target_dir = target_dir.resolve()
    for member in zip_file.infolist():
        member_path = (target_dir / member.filename).resolve()
        if member_path != target_dir and target_dir not in member_path.parents:
            raise ValueError(
                f"Refusing to extract unsafe path outside target directory: {member.filename!r}"
            )
    zip_file.extractall(target_dir)


def apply_update_from_repo(repo, branch, force=False):
    """
    Download and apply the latest repository snapshot into this script folder.
    Existing files are overwritten, missing files are created, and no files are deleted.
    """
    state = _load_update_state()
    state_key = f"{repo}@{branch}"
    local_sha = state.get(state_key)

    try:
        remote_sha = _fetch_latest_commit_sha(repo, branch)
    except urllib.error.URLError as exc:
        print(f"Update check failed: {exc}", file=sys.stderr)
        return False
    except (KeyError, json.JSONDecodeError) as exc:
        print(f"Update check failed: unexpected API response ({exc})", file=sys.stderr)
        return False

    if not force and local_sha == remote_sha:
        print(f"Already up to date at {remote_sha[:7]} ({repo}:{branch}).")
        return True

    root = _script_root()
    with tempfile.TemporaryDirectory(prefix="tinyscript-update-") as tmpdir:
        zip_path = Path(tmpdir) / "repo.zip"
        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            _download_zipball(repo, branch, zip_path)
        except urllib.error.URLError as exc:
            print(f"Download failed: {exc}", file=sys.stderr)
            return False

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                _safe_extract(zf, extract_dir)
        except (OSError, zipfile.BadZipFile, ValueError) as exc:
            print(f"Update extraction failed: {exc}", file=sys.stderr)
            return False

        extracted_roots = [p for p in extract_dir.iterdir() if p.is_dir()]
        if not extracted_roots:
            print("Update failed: downloaded archive had no project contents.", file=sys.stderr)
            return False
        repo_root = extracted_roots[0]

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

    state[state_key] = remote_sha
    _save_update_state(state)
    print(
        f"Update applied from {repo}:{branch} ({remote_sha[:7]}). "
        f"Updated {updated_count} file(s), added {added_count} file(s)."
    )
    return True


class TinyScript:
    """Main compiler/interpreter for TinyScript"""
    
    def __init__(self, optimize=True):
        self.optimize_enabled = optimize
        self.interpreter = Interpreter()
        self.optimizer = Optimizer()
    
    def compile_and_run(self, source_code, show_tokens=False, show_ast=False, capture_output=False):
        """Compile and execute TinyScript code; return True if execution finished cleanly."""
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
        """Pretty print the AST"""
        from parser import BlockNode
        
        prefix = "  " * indent
        
        if isinstance(node, BlockNode):
            print(f"{prefix}Block:")
            for stmt in node.statements:
                self._print_ast(stmt, indent + 1)
        else:
            print(f"{prefix}{node}")
    
    def run_file(self, filename, show_tokens=False, show_ast=False):
        """Run a TinyScript file; return True on success."""
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
        """Interactive Read-Eval-Print Loop"""
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
    """Main entry point"""
    argp = argparse.ArgumentParser(description='TinyScript Compiler/Interpreter')
    argp.add_argument('file', nargs='?', help='TinyScript file to run')
    argp.add_argument('--no-optimize', action='store_true', help='Disable optimization')
    argp.add_argument('--show-tokens', action='store_true', help='Show tokens')
    argp.add_argument('--show-ast', action='store_true', help='Show AST')
    argp.add_argument('--repl', action='store_true', help='Start interactive REPL')
    argp.add_argument('--self-update', action='store_true', help='Download and apply newest files if repository has a new commit')
    argp.add_argument('--auto-update', action='store_true', help='Check/update before running file or REPL')
    argp.add_argument('--force-update', action='store_true', help='Apply update even if commit SHA appears unchanged')
    argp.add_argument('--update-repo', default='Gun-spec/TinyLang', help='GitHub repo for updater (owner/name)')
    argp.add_argument('--update-branch', default='main', help='Branch to pull updates from')
    
    args = argp.parse_args()

    if args.self_update or args.auto_update:
        ok = apply_update_from_repo(
            repo=args.update_repo,
            branch=args.update_branch,
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
