"""
Lexer: Breaks source code into tokens (words and symbols)
Think of it like breaking a sentence into individual words
"""

import re
from enum import Enum, auto

class TokenType(Enum):
    """All the types of tokens our language recognizes"""
    # Literals
    NUMBER = auto()      # 123, 45.67
    IDENTIFIER = auto()  # variable names like x, count
    STRING = auto()      # "hello world"
    
    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNC = auto()
    RETURN = auto()
    PRINT = auto()
    
    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    MULTIPLY = auto()    # *
    DIVIDE = auto()      # /
    ASSIGN = auto()      # =
    EQUAL = auto()       # ==
    NOT_EQUAL = auto()   # !=
    LESS = auto()        # <
    GREATER = auto()     # >
    LESS_EQ = auto()     # <=
    GREATER_EQ = auto()  # >=
    
    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    COMMA = auto()       # ,
    SEMICOLON = auto()   # ;
    
    # Special
    EOF = auto()         # End of file
    NEWLINE = auto()     # Line break

class Token:
    """A single token with its type and value"""
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, {self.line}:{self.column})'

class Lexer:
    """Converts source code text into a list of tokens"""
    
    # Keywords in our language
    KEYWORDS = {
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'func': TokenType.FUNC,
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
    }
    
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def current_char(self):
        """Get the character at current position"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset=1):
        """Look ahead at the next character without moving forward"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        """Move to the next character"""
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        """Skip spaces and tabs (but not newlines)"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip comments that start with #"""
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self):
        """Read a number (integer or float)"""
        start_col = self.column
        num_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # Second dot, stop here
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        value = float(num_str) if has_dot else int(num_str)
        return Token(TokenType.NUMBER, value, self.line, start_col)
    
    def read_identifier(self):
        """Read an identifier or keyword"""
        start_col = self.column
        id_str = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str, self.line, start_col)
    
    def read_string(self):
        """Read a string literal"""
        start_col = self.column
        self.advance()  # Skip opening quote
        string_val = ''
        
        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\\':
                self.advance()
                # Handle escape sequences
                if self.current_char() == 'n':
                    string_val += '\n'
                elif self.current_char() == 't':
                    string_val += '\t'
                elif self.current_char() == '"':
                    string_val += '"'
                else:
                    string_val += self.current_char()
                self.advance()
            else:
                string_val += self.current_char()
                self.advance()
        
        if self.current_char() == '"':
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, string_val, self.line, start_col)
    
    def tokenize(self):
        """Convert the entire source code into tokens"""
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Comments
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Newlines
            if self.current_char() == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.tokens.append(token)
                self.advance()
                continue
            
            # Numbers
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Strings
            if self.current_char() == '"':
                self.tokens.append(self.read_string())
                continue
            
            # Two-character operators
            char = self.current_char()
            next_char = self.peek_char()
            start_col = self.column
            
            if char == '=' and next_char == '=':
                self.tokens.append(Token(TokenType.EQUAL, '==', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '!' and next_char == '=':
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '<' and next_char == '=':
                self.tokens.append(Token(TokenType.LESS_EQ, '<=', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '>' and next_char == '=':
                self.tokens.append(Token(TokenType.GREATER_EQ, '>=', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            # Single-character tokens
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS,
                '>': TokenType.GREATER,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
            }
            
            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, self.line, start_col))
                self.advance()
                continue
            
            # Unknown character
            raise SyntaxError(f"Unknown character '{char}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

# Test the lexer
if __name__ == '__main__':
    code = """
    # This is a comment
    x = 10
    y = 20.5
    name = "Alice"
    
    if x < y {
        print("x is less")
    }
    
    func add(a, b) {
        return a + b
    }
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print("Tokens generated:")
    for token in tokens:
        if token.type != TokenType.NEWLINE:  # Skip newlines for cleaner output
            print(token)
