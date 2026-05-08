"""
Optimizer: Makes the AST more efficient before execution
This is like cleaning up your code to run faster
"""

from parser import *

class Optimizer:
    """Optimizes the Abstract Syntax Tree"""
    
    def optimize(self, node):
        """Optimize a node and its children"""
        method_name = f'optimize_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_optimize)
        return method(node)
    
    def generic_optimize(self, node):
        """Default: return node unchanged"""
        return node
    
    def optimize_BlockNode(self, node):
        """Optimize all statements in a block"""
        optimized_stmts = []
        for stmt in node.statements:
            optimized = self.optimize(stmt)
            # Remove statements that do nothing
            if optimized is not None:
                optimized_stmts.append(optimized)
        return BlockNode(optimized_stmts)
    
    def optimize_BinaryOpNode(self, node):
        """Constant folding: evaluate expressions at compile time"""
        left = self.optimize(node.left)
        right = self.optimize(node.right)
        
        # If both sides are constants, compute the result now
        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            op = node.operator
            l_val = left.value
            r_val = right.value
            
            try:
                if op == '+':
                    return NumberNode(l_val + r_val)
                elif op == '-':
                    return NumberNode(l_val - r_val)
                elif op == '*':
                    return NumberNode(l_val * r_val)
                elif op == '/':
                    if r_val != 0:
                        return NumberNode(l_val / r_val)
                elif op == '==':
                    return NumberNode(1 if l_val == r_val else 0)
                elif op == '!=':
                    return NumberNode(1 if l_val != r_val else 0)
                elif op == '<':
                    return NumberNode(1 if l_val < r_val else 0)
                elif op == '>':
                    return NumberNode(1 if l_val > r_val else 0)
                elif op == '<=':
                    return NumberNode(1 if l_val <= r_val else 0)
                elif op == '>=':
                    return NumberNode(1 if l_val >= r_val else 0)
            except:
                pass  # If computation fails, keep original
        
        # Algebraic simplifications
        if node.operator == '+':
            # x + 0 = x
            if isinstance(right, NumberNode) and right.value == 0:
                return left
            # 0 + x = x
            if isinstance(left, NumberNode) and left.value == 0:
                return right
        
        elif node.operator == '-':
            # x - 0 = x
            if isinstance(right, NumberNode) and right.value == 0:
                return left
            # x - x = 0 (if x is a simple variable)
            if isinstance(left, VariableNode) and isinstance(right, VariableNode):
                if left.name == right.name:
                    return NumberNode(0)
        
        elif node.operator == '*':
            # x * 0 = 0
            if isinstance(right, NumberNode) and right.value == 0:
                return NumberNode(0)
            if isinstance(left, NumberNode) and left.value == 0:
                return NumberNode(0)
            # x * 1 = x
            if isinstance(right, NumberNode) and right.value == 1:
                return left
            # 1 * x = x
            if isinstance(left, NumberNode) and left.value == 1:
                return right
        
        elif node.operator == '/':
            # x / 1 = x
            if isinstance(right, NumberNode) and right.value == 1:
                return left
        
        return BinaryOpNode(left, node.operator, right)
    
    def optimize_UnaryOpNode(self, node):
        """Optimize unary operations"""
        operand = self.optimize(node.operand)
        
        # Constant folding for unary operations
        if isinstance(operand, NumberNode):
            if node.operator == '-':
                return NumberNode(-operand.value)
            elif node.operator == '+':
                return NumberNode(+operand.value)
        
        # Double negation elimination: --x = x
        if node.operator == '-' and isinstance(operand, UnaryOpNode):
            if operand.operator == '-':
                return operand.operand
        
        return UnaryOpNode(node.operator, operand)
    
    def optimize_AssignNode(self, node):
        """Optimize assignment"""
        value = self.optimize(node.value)
        return AssignNode(node.name, value)
    
    def optimize_IfNode(self, node):
        """Optimize if statements"""
        condition = self.optimize(node.condition)
        then_block = self.optimize(node.then_block)
        else_block = self.optimize(node.else_block) if node.else_block else None
        
        # Constant condition elimination
        if isinstance(condition, NumberNode):
            if condition.value:
                # Condition is always true, return only then block
                return then_block
            else:
                # Condition is always false, return else block (or nothing)
                return else_block
        
        return IfNode(condition, then_block, else_block)
    
    def optimize_WhileNode(self, node):
        """Optimize while loops"""
        condition = self.optimize(node.condition)
        body = self.optimize(node.body)
        
        # Dead loop elimination
        if isinstance(condition, NumberNode) and not condition.value:
            # While false { ... } never executes
            return None
        
        return WhileNode(condition, body)
    
    def optimize_FunctionDefNode(self, node):
        """Optimize function definitions"""
        body = self.optimize(node.body)
        return FunctionDefNode(node.name, node.params, body)
    
    def optimize_FunctionCallNode(self, node):
        """Optimize function calls"""
        args = [self.optimize(arg) for arg in node.args]
        return FunctionCallNode(node.name, args)
    
    def optimize_ReturnNode(self, node):
        """Optimize return statements"""
        value = self.optimize(node.value)
        return ReturnNode(value)
    
    def optimize_PrintNode(self, node):
        """Optimize print statements"""
        value = self.optimize(node.value)
        return PrintNode(value)

# Demonstrate the optimizer
if __name__ == '__main__':
    from lexer import Lexer
    from parser import Parser
    from interpreter import Interpreter
    
    code = """
    # This code has lots of inefficiencies
    x = 5 + 0          # x + 0 = x
    y = x * 1          # x * 1 = x
    z = 10 - 0         # x - 0 = x
    w = 2 + 3          # Can be computed at compile time
    
    # Dead code
    if 0 {
        print("This never runs")
    }
    
    # Always true
    if 1 {
        print("This always runs")
    }
    
    result = --5       # Double negation
    print(result)
    """
    
    print("Original code:")
    print(code)
    print("\n" + "=" * 50)
    
    # Parse
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("\nOriginal AST statements:")
    for stmt in ast.statements:
        print(f"  {stmt}")
    
    # Optimize
    optimizer = Optimizer()
    optimized_ast = optimizer.optimize(ast)
    
    print("\nOptimized AST statements:")
    for stmt in optimized_ast.statements:
        print(f"  {stmt}")
    
    # Run optimized version
    print("\n" + "=" * 50)
    print("Running optimized code:")
    interpreter = Interpreter()
    interpreter.run(optimized_ast)
