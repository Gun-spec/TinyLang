"""
Interpreter: Executes the Abstract Syntax Tree
This is where your code actually runs!
"""

from parser import *
from errors import TinyScriptRuntimeError


class ReturnValue(Exception):
    """Special exception to handle return statements"""
    def __init__(self, value, *, line=None, column=None):
        self.value = value
        self.line = line
        self.column = column


def _repr_type(value):
    if isinstance(value, bool):
        return 'bool'
    if isinstance(value, int) and not isinstance(value, bool):
        return 'int'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, Function):
        return 'function'
    return type(value).__name__


def _truthy(condition):
    return bool(condition)


class Environment:
    """Stores variables and their values"""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    
    def define(self, name, value):
        """Define a new variable"""
        self.vars[name] = value
    
    def get(self, name):
        """Get a variable's value"""
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise KeyError(name)
    
    def set(self, name, value):
        """Set an existing variable or create new one"""
        self.vars[name] = value


class Function:
    """Represents a user-defined function"""
    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env
    
    def __repr__(self):
        return f'<function {self.name}>'

class Interpreter:
    """Executes the AST"""
    
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.call_depth = 0
        self.max_call_depth = 150  # Guard: each TinyScript call spans several Python frames
    
    def run(self, ast):
        """Execute the entire program"""
        try:
            return self.visit(ast, self.global_env)
        except ReturnValue as ret:
            raise TinyScriptRuntimeError(
                "'return' used outside of a function",
                line=ret.line,
                column=ret.column,
            )
        except RecursionError:
            # Defense in depth: never leak a raw Python traceback to users
            raise TinyScriptRuntimeError(
                "Maximum recursion depth exceeded while running program"
            )
    
    def visit(self, node, env):
        """Visit a node and execute it"""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node, env)
    
    def generic_visit(self, node, env):
        raise TinyScriptRuntimeError(
            f"Internal error: unsupported syntax node '{type(node).__name__}'"
        )
    
    def visit_BlockNode(self, node, env):
        """Execute a block of statements"""
        result = None
        for stmt in node.statements:
            result = self.visit(stmt, env)
        return result
    
    def visit_NumberNode(self, node, env):
        """Return the number value"""
        return node.value
    
    def visit_StringNode(self, node, env):
        """Return the string value"""
        return node.value
    
    def visit_VariableNode(self, node, env):
        """Get variable value"""
        try:
            return env.get(node.name)
        except KeyError:
            raise TinyScriptRuntimeError(
                f"Undefined variable '{node.name}'",
                line=node.line,
                column=node.column,
            )
    
    def visit_BinaryOpNode(self, node, env):
        """Execute binary operations"""
        left = self.visit(node.left, env)
        right = self.visit(node.right, env)
        op = node.operator

        try:
            if op == '+':
                # String concatenation: either side a string => concatenate
                if isinstance(left, str) or isinstance(right, str):
                    if not (isinstance(left, str) and isinstance(right, str)):
                        raise TinyScriptRuntimeError(
                            f"Cannot concatenate string with {_repr_type(right if isinstance(left, str) else left)}; "
                            f"convert explicitly first",
                            line=node.line,
                            column=node.column,
                        )
                    return left + right
                return left + right
            if op == '-':
                return left - right
            if op == '*':
                # String repetition: "ab" * 3
                if isinstance(left, str) and isinstance(right, int) and not isinstance(right, bool):
                    if right < 0:
                        raise TinyScriptRuntimeError(
                            'String repetition count must be >= 0',
                            line=node.line,
                            column=node.column,
                        )
                    return left * right
                return left * right
            if op == '/':
                if right == 0:
                    raise TinyScriptRuntimeError(
                        'Division by zero',
                        line=node.line,
                        column=node.column,
                    )
                return left / right
            if op == '%':
                if right == 0:
                    raise TinyScriptRuntimeError(
                        'Modulo by zero',
                        line=node.line,
                        column=node.column,
                    )
                return left % right
            if op == '==':
                return left == right
            if op == '!=':
                return left != right
            if op == '<':
                return left < right
            if op == '>':
                return left > right
            if op == '<=':
                return left <= right
            if op == '>=':
                return left >= right
        except TinyScriptRuntimeError:
            raise
        except TypeError as e:
            raise TinyScriptRuntimeError(
                f"Invalid operands for '{op}': {_repr_type(left)} and {_repr_type(right)} ({e})",
                line=node.line,
                column=node.column,
            )
        raise TinyScriptRuntimeError(
            f"Unknown operator: {op!r}",
            line=node.line,
            column=node.column,
        )

    def visit_UnaryOpNode(self, node, env):
        """Execute unary operations"""
        operand = self.visit(node.operand, env)
        try:
            if node.operator == '-':
                return -operand
            if node.operator == '+':
                return +operand
        except TypeError as e:
            raise TinyScriptRuntimeError(
                f"Invalid operand for unary {node.operator!r}: {_repr_type(operand)} ({e})",
                line=node.line,
                column=node.column,
            )
        raise TinyScriptRuntimeError(
            f"Unknown unary operator: {node.operator!r}",
            line=node.line,
            column=node.column,
        )
    
    def visit_AssignNode(self, node, env):
        """Execute variable assignment"""
        value = self.visit(node.value, env)
        env.set(node.name, value)
        return value
    
    def visit_IfNode(self, node, env):
        """Execute if statement"""
        condition = self.visit(node.condition, env)
        
        if _truthy(condition):
            return self.visit(node.then_block, env)
        if node.else_block:
            return self.visit(node.else_block, env)
        
        return None
    
    def visit_WhileNode(self, node, env):
        """Execute while loop"""
        result = None
        while _truthy(self.visit(node.condition, env)):
            result = self.visit(node.body, env)
        return result
    
    def visit_FunctionDefNode(self, node, env):
        """Define a function"""
        func = Function(node.name, node.params, node.body, env)
        env.set(node.name, func)
        return func
    
    def visit_FunctionCallNode(self, node, env):
        """Call a function"""
        try:
            func = env.get(node.name)
        except KeyError:
            raise TinyScriptRuntimeError(
                f"Undefined function '{node.name}'",
                line=node.line,
                column=node.column,
            )
        
        if not isinstance(func, Function):
            raise TinyScriptRuntimeError(
                f"'{node.name}' is not callable (got {_repr_type(func)})",
                line=node.line,
                column=node.column,
            )
        
        args = []
        try:
            for arg in node.args:
                args.append(self.visit(arg, env))
        except TinyScriptRuntimeError:
            raise

        if len(args) != len(func.params):
            raise TinyScriptRuntimeError(
                f"Function '{func.name}' expects {len(func.params)} argument(s), got {len(args)}",
                line=node.line,
                column=node.column,
            )
        
        func_env = Environment(func.closure_env)
        
        for param, arg in zip(func.params, args):
            func_env.define(param, arg)
        
        self.call_depth += 1
        try:
            if self.call_depth > self.max_call_depth:
                raise TinyScriptRuntimeError(
                    f"Maximum recursion depth exceeded ({self.max_call_depth}) "
                    f"while calling '{func.name}' at line {node.line}, column {node.column}",
                    line=node.line,
                    column=node.column,
                )
            try:
                self.visit(func.body, func_env)
                return None
            except ReturnValue as ret:
                return ret.value
        finally:
            self.call_depth -= 1
    
    def visit_ReturnNode(self, node, env):
        """Execute return statement"""
        value = self.visit(node.value, env)
        raise ReturnValue(value, line=node.line, column=node.column)
    
    def visit_PrintNode(self, node, env):
        """Execute print statement"""
        value = self.visit(node.value, env)
        print(value)
        return value

# Test the interpreter
if __name__ == '__main__':
    from lexer import Lexer
    from parser import Parser
    
    code = """
    # Basic arithmetic
    x = 10
    y = 20
    z = x + y * 2
    print(z)
    
    # Conditionals
    if x < y {
        print("x is less than y")
    } else {
        print("x is not less than y")
    }
    
    # Functions
    func add(a, b) {
        return a + b
    }
    
    func factorial(n) {
        if n <= 1 {
            return 1
        } else {
            return n * factorial(n - 1)
        }
    }
    
    result = add(5, 3)
    print(result)
    
    fact = factorial(5)
    print(fact)
    
    # Loops
    counter = 0
    while counter < 5 {
        print(counter)
        counter = counter + 1
    }
    """
    
    print("Running TinyScript program:")
    print("=" * 50)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.run(ast)
