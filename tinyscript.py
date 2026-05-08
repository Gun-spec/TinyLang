"""
TinyScript Compiler and Interpreter
Main entry point for the language
"""

import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from optimizer import Optimizer

class TinyScript:
    """Main compiler/interpreter for TinyScript"""
    
    def __init__(self, optimize=True):
        self.optimize_enabled = optimize
        self.interpreter = Interpreter()
        self.optimizer = Optimizer()
    
    def compile_and_run(self, source_code, show_tokens=False, show_ast=False):
        """Compile and execute TinyScript code"""
        try:
            # Step 1: Lexical Analysis (Tokenization)
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
            
            # Step 2: Parsing (Build AST)
            parser = Parser(tokens)
            ast = parser.parse()
            
            if show_ast:
                print("=" * 60)
                print("ABSTRACT SYNTAX TREE:")
                print("=" * 60)
                self._print_ast(ast, indent=0)
                print()
            
            # Step 3: Optimization (if enabled)
            if self.optimize_enabled:
                ast = self.optimizer.optimize(ast)
                if show_ast:
                    print("=" * 60)
                    print("OPTIMIZED AST:")
                    print("=" * 60)
                    self._print_ast(ast, indent=0)
                    print()
            
            # Step 4: Interpretation (Execute)
            print("=" * 60)
            print("OUTPUT:")
            print("=" * 60)
            result = self.interpreter.run(ast)
            
            return result
            
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return None
        except NameError as e:
            print(f"Name Error: {e}")
            return None
        except Exception as e:
            print(f"Runtime Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
        """Run a TinyScript file"""
        try:
            with open(filename, 'r') as f:
                source_code = f.read()
            
            print(f"Running {filename}...")
            print()
            return self.compile_and_run(source_code, show_tokens, show_ast)
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return None
    
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
                
                if line.strip() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if not line.strip():
                    continue
                
                # Execute the line
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
    import argparse
    
    parser = argparse.ArgumentParser(description='TinyScript Compiler/Interpreter')
    parser.add_argument('file', nargs='?', help='TinyScript file to run')
    parser.add_argument('--no-optimize', action='store_true', help='Disable optimization')
    parser.add_argument('--show-tokens', action='store_true', help='Show tokens')
    parser.add_argument('--show-ast', action='store_true', help='Show AST')
    parser.add_argument('--repl', action='store_true', help='Start interactive REPL')
    
    args = parser.parse_args()
    
    # Create compiler
    compiler = TinyScript(optimize=not args.no_optimize)
    
    if args.repl or not args.file:
        # Start REPL if no file given or --repl flag
        compiler.repl()
    else:
        # Run file
        compiler.run_file(args.file, args.show_tokens, args.show_ast)

if __name__ == '__main__':
    main()
