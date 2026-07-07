"""
Parser: Takes tokens and builds an Abstract Syntax Tree (AST)
The AST represents the structure of your program
"""

from lexer import TokenType

# ============== AST Node Classes ==============
# These represent different parts of your program

class ASTNode:
    """Base class for all AST nodes"""
    pass

class NumberNode(ASTNode):
    """A number like 42 or 3.14"""
    def __init__(self, value, *, line=None, column=None):
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Number({self.value})'

class StringNode(ASTNode):
    """A string like "hello" """
    def __init__(self, value, *, line=None, column=None):
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'String({self.value!r})'

class VariableNode(ASTNode):
    """A variable name like x or count"""
    def __init__(self, name, *, line=None, column=None):
        self.name = name
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Var({self.name})'

class BinaryOpNode(ASTNode):
    """An operation with two operands like a + b"""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f'BinOp({self.left} {self.operator} {self.right})'

class UnaryOpNode(ASTNode):
    """An operation with one operand like -x"""
    def __init__(self, operator, operand, *, line=None, column=None):
        self.operator = operator
        self.operand = operand
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'UnaryOp({self.operator} {self.operand})'

class AssignNode(ASTNode):
    """Variable assignment like x = 10"""
    def __init__(self, name, value, *, line=None, column=None):
        self.name = name
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Assign({self.name} = {self.value})'

class IfNode(ASTNode):
    """If statement"""
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    
    def __repr__(self):
        return f'If({self.condition})'

class WhileNode(ASTNode):
    """While loop"""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f'While({self.condition})'

class FunctionDefNode(ASTNode):
    """Function definition"""
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f'FuncDef({self.name})'

class FunctionCallNode(ASTNode):
    """Function call like add(1, 2)"""
    def __init__(self, name, args, *, line=None, column=None):
        self.name = name
        self.args = args
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Call({self.name})'

class ReturnNode(ASTNode):
    """Return statement"""
    def __init__(self, value, *, line=None, column=None):
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Return({self.value})'

class PrintNode(ASTNode):
    """Print statement"""
    def __init__(self, value, *, line=None, column=None):
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Print({self.value})'

class BlockNode(ASTNode):
    """A block of statements"""
    def __init__(self, statements):
        self.statements = statements
    
    def __repr__(self):
        return f'Block({len(self.statements)} stmts)'

# ============== Parser ==============

class Parser:
    """Converts tokens into an Abstract Syntax Tree"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self):
        """Get current token"""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek_token(self, offset=1):
        """Look ahead at next token"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def _advance_to_index_skip_newlines(self, idx):
        """Clamp index within tokens and skip NEWLINE-only gap."""
        if idx >= len(self.tokens):
            return len(self.tokens) - 1
        while idx < len(self.tokens) and self.tokens[idx].type == TokenType.NEWLINE:
            idx += 1
        if idx >= len(self.tokens):
            return len(self.tokens) - 1
        return idx
    
    def next_meaningful_token(self, start_offset=1):
        """First non-NEWLINE token after current + start_offset (does not move pos)."""
        idx = self._advance_to_index_skip_newlines(self.pos + start_offset)
        return self.tokens[idx]
    
    def advance(self):
        """Move to next token"""
        self.pos += 1
    
    def expect(self, token_type):
        """Ensure current token matches expected type, then advance"""
        token = self.current_token()
        if token.type != token_type:
            exp = getattr(token_type, 'name', str(token_type))
            got = getattr(token.type, 'name', str(token.type))
            raise SyntaxError(f"Expected {exp}, got {got} at line {token.line}, column {token.column}")
        self.advance()
        return token
    
    def skip_newlines(self):
        """Skip any newline tokens"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()

    def skip_optional_semicolon(self):
        """Allow an optional trailing semicolon after a statement."""
        self.skip_newlines()
        if self.current_token().type == TokenType.SEMICOLON:
            self.advance()
            self.skip_newlines()
    
    def parse(self):
        """Parse the entire program"""
        statements = []
        self.skip_newlines()
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return BlockNode(statements)
    
    def parse_statement(self):
        """Parse a single statement"""
        self.skip_newlines()
        while self.current_token().type == TokenType.SEMICOLON:
            self.advance()
            self.skip_newlines()
        token = self.current_token()
        if token.type == TokenType.EOF:
            return None
        
        if token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.FUNC:
            return self.parse_function_def()
        elif token.type == TokenType.RETURN:
            return self.parse_return()
        elif token.type == TokenType.PRINT:
            return self.parse_print()
        elif token.type == TokenType.IDENTIFIER:
            lookahead = self.next_meaningful_token(1)
            if lookahead.type == TokenType.ASSIGN:
                return self.parse_assignment()
            if lookahead.type == TokenType.LPAREN:
                call = self.parse_function_call()
                self.skip_optional_semicolon()
                return call
            expr = self.parse_expression()
            self.skip_optional_semicolon()
            return expr
        elif token.type == TokenType.LBRACE:
            return self.parse_block()
        else:
            expr = self.parse_expression()
            self.skip_optional_semicolon()
            return expr
    
    def parse_assignment(self):
        """Parse variable assignment: x = 10"""
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.skip_newlines()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.skip_optional_semicolon()
        return AssignNode(
            name_tok.value,
            value,
            line=name_tok.line,
            column=name_tok.column,
        )
    
    def parse_if(self):
        """Parse if statement"""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.skip_newlines()
        then_block = self.parse_block()
        self.skip_newlines()
        
        else_block = None
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            self.skip_newlines()
            else_block = self.parse_block()
        
        return IfNode(condition, then_block, else_block)
    
    def parse_while(self):
        """Parse while loop"""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.skip_newlines()
        body = self.parse_block()
        return WhileNode(condition, body)
    
    def parse_function_def(self):
        """Parse function definition"""
        self.expect(TokenType.FUNC)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        params = []
        seen = set()
        self.skip_newlines()
        if self.current_token().type != TokenType.RPAREN:
            first_param = self.expect(TokenType.IDENTIFIER)
            if first_param.value in seen:
                raise SyntaxError(
                    f"Duplicate parameter name '{first_param.value}' "
                    f"at line {first_param.line}, column {first_param.column}"
                )
            seen.add(first_param.value)
            params.append(first_param.value)
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
                p_tok = self.expect(TokenType.IDENTIFIER)
                if p_tok.value in seen:
                    raise SyntaxError(
                        f"Duplicate parameter name '{p_tok.value}' "
                        f"at line {p_tok.line}, column {p_tok.column}"
                    )
                seen.add(p_tok.value)
                params.append(p_tok.value)

        self.skip_newlines()
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        body = self.parse_block()

        return FunctionDefNode(name, params, body)

    def parse_function_call(self):
        """Parse function call"""
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.skip_newlines()
        self.expect(TokenType.LPAREN)

        args = []
        self.skip_newlines()
        if self.current_token().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
                args.append(self.parse_expression())

        self.skip_newlines()
        self.expect(TokenType.RPAREN)
        return FunctionCallNode(
            name_tok.value,
            args,
            line=name_tok.line,
            column=name_tok.column,
        )
    
    def parse_return(self):
        """Parse return statement"""
        kw = self.current_token()
        self.expect(TokenType.RETURN)
        self.skip_newlines()
        value = self.parse_expression()
        self.skip_optional_semicolon()
        return ReturnNode(value, line=kw.line, column=kw.column)
    
    def parse_print(self):
        """Parse print statement"""
        kw = self.current_token()
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        self.skip_newlines()
        value = self.parse_expression()
        self.skip_newlines()
        self.expect(TokenType.RPAREN)
        self.skip_optional_semicolon()
        return PrintNode(value, line=kw.line, column=kw.column)
    
    def parse_block(self):
        """Parse a block of statements { ... }"""
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        statements = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return BlockNode(statements)
    
    def parse_expression(self):
        """Parse an expression (uses precedence climbing)"""
        self.skip_newlines()
        return self.parse_comparison()
    
    def parse_comparison(self):
        """Parse comparison operators: ==, !=, <, >, <=, >="""
        self.skip_newlines()
        left = self.parse_additive()
        
        while self.current_token().type in [
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS, TokenType.GREATER,
            TokenType.LESS_EQ, TokenType.GREATER_EQ
        ]:
            op = self.current_token().value
            self.advance()
            self.skip_newlines()
            right = self.parse_additive()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_additive(self):
        """Parse + and - operators"""
        self.skip_newlines()
        left = self.parse_multiplicative()
        
        while self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token().value
            self.advance()
            self.skip_newlines()
            right = self.parse_multiplicative()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_multiplicative(self):
        """Parse * and / operators"""
        self.skip_newlines()
        left = self.parse_unary()
        
        while self.current_token().type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op = self.current_token().value
            self.advance()
            self.skip_newlines()
            right = self.parse_unary()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_unary(self):
        """Parse unary operators like -x"""
        self.skip_newlines()
        if self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op_tok = self.current_token()
            op = op_tok.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(op, operand, line=op_tok.line, column=op_tok.column)
        
        return self.parse_primary()
    
    def parse_primary(self):
        """Parse primary expressions: numbers, strings, variables, function calls"""
        self.skip_newlines()
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value, line=token.line, column=token.column)
        
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.value, line=token.line, column=token.column)
        
        elif token.type == TokenType.IDENTIFIER:
            next_tok = self.next_meaningful_token(1)
            if next_tok.type == TokenType.LPAREN:
                return self.parse_function_call()
            self.advance()
            return VariableNode(token.value, line=token.line, column=token.column)
        
        elif token.type == TokenType.LPAREN:
            self.advance()
            self.skip_newlines()
            expr = self.parse_expression()
            self.skip_newlines()
            self.expect(TokenType.RPAREN)
            return expr
        
        elif token.type == TokenType.EOF:
            raise SyntaxError(f"Unexpected end of input at line {token.line}, column {token.column}")
        
        else:
            got = getattr(token.type, 'name', str(token.type))
            raise SyntaxError(f"Unexpected token {got} at line {token.line}, column {token.column}")

# Test the parser
if __name__ == '__main__':
    from lexer import Lexer
    
    code = """
    x = 10
    y = 20
    
    if x < y {
        print("x is less")
    }
    
    func add(a, b) {
        return a + b
    }
    
    result = add(x, y)
    print(result)
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("Abstract Syntax Tree:")
    print(ast)
    print("\nStatements:")
    for stmt in ast.statements:
        print(f"  {stmt}")
