"""
Interpreter: Executes the Abstract Syntax Tree
This is where your code actually runs!
"""

from parser import *

class ReturnValue(Exception):
    """Special exception to handle return statements"""
    def __init__(self, value):
        self.value = value

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
            raise NameError(f"Undefined variable: {name}")
    
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
    
    def run(self, ast):
        """Execute the entire program"""
        return self.visit(ast, self.global_env)
    
    def visit(self, node, env):
        """Visit a node and execute it"""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node, env)
    
    def generic_visit(self, node, env):
        """Fallback for unimplemented nodes"""
        raise Exception(f'No visit method for {type(node).__name__}')
    
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
        return env.get(node.name)
    
    def visit_BinaryOpNode(self, node, env):
        """Execute binary operations"""
        left = self.visit(node.left, env)
        right = self.visit(node.right, env)
        
        op = node.operator
        
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        else:
            raise Exception(f"Unknown operator: {op}")
    
    def visit_UnaryOpNode(self, node, env):
        """Execute unary operations"""
        operand = self.visit(node.operand, env)
        
        if node.operator == '-':
            return -operand
        elif node.operator == '+':
            return +operand
        else:
            raise Exception(f"Unknown unary operator: {node.operator}")
    
    def visit_AssignNode(self, node, env):
        """Execute variable assignment"""
        value = self.visit(node.value, env)
        env.set(node.name, value)
        return value
    
    def visit_IfNode(self, node, env):
        """Execute if statement"""
        condition = self.visit(node.condition, env)
        
        if condition:
            return self.visit(node.then_block, env)
        elif node.else_block:
            return self.visit(node.else_block, env)
        
        return None
    
    def visit_WhileNode(self, node, env):
        """Execute while loop"""
        result = None
        while self.visit(node.condition, env):
            result = self.visit(node.body, env)
        return result
    
    def visit_FunctionDefNode(self, node, env):
        """Define a function"""
        func = Function(node.name, node.params, node.body, env)
        env.set(node.name, func)
        return func
    
    def visit_FunctionCallNode(self, node, env):
        """Call a function"""
        func = env.get(node.name)
        
        if not isinstance(func, Function):
            raise TypeError(f"{node.name} is not a function")
        
        # Evaluate arguments
        args = [self.visit(arg, env) for arg in node.args]
        
        # Check argument count
        if len(args) != len(func.params):
            raise TypeError(f"{func.name} expects {len(func.params)} arguments, got {len(args)}")
        
        # Create new environment for function
        func_env = Environment(func.closure_env)
        
        # Bind parameters to arguments
        for param, arg in zip(func.params, args):
            func_env.define(param, arg)
        
        # Execute function body
        try:
            self.visit(func.body, func_env)
            return None  # No explicit return
        except ReturnValue as ret:
            return ret.value
    
    def visit_ReturnNode(self, node, env):
        """Execute return statement"""
        value = self.visit(node.value, env)
        raise ReturnValue(value)
    
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
