"""
TinyScript Compiler and Interpreter
Main entry point for the language
"""

import argparse
import io
import sys

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from optimizer import Optimizer
from errors import TinyScriptRuntimeError

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
    
    args = argp.parse_args()
    
    compiler = TinyScript(optimize=not args.no_optimize)
    
    if args.repl or not args.file:
        compiler.repl()
        sys.exit(0)

    sys.exit(0 if compiler.run_file(args.file, args.show_tokens, args.show_ast) else 1)


if __name__ == '__main__':
    main()
