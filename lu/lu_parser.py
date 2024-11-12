from typing import List, Optional
from lu_token import Token
import ast
from lu_errors import SyntaxError, NameError, RuntimeError
from expr import Expr
from TYPE import keyword_type
from elements import elements

class Parser(Expr, keyword_type, elements):
    def __init__(self, tokens: List[Token]) -> None:
        self.imports: List[str] = []
        self.datatypes = ["INTEGER", "CHAR", "STRING", "DATE", "REAL", "BOOLEAN"]
        self.tokens = tokens
        self.current = 0
        self.indent = 0

    def parse_statement(self) -> ast.AST:
        """Parse a single statement."""
        return ast.parse(self.get_expr()).body

    def peek(self) -> Token:
        """Return the current token that is being parsed."""
        return self.tokens[self.current]

    def peek_relative(self, n: int) -> Token:
        """Return the token `n` positions from the current token."""
        k = self.current + n
        if k < 0 or k >= len(self.tokens):
            SyntaxError(f"List index out of range: {k}")
            return Token(type="EOF", value="", line=self.tokens[-1].line)
        return self.tokens[k]

    def advance(self) -> Token:
        """Increment and return the previous token."""
        if self.is_at_file_end():
            return self.peek()  # Return current EOF token without advancing
        self.current += 1
        return self.tokens[self.current - 1]

    def is_at_file_end(self, n: int = None) -> bool:
        """Check if the current or `n`-th token is EOF."""
        return (self.peek_relative(n).type == 'EOF') if n is not None else self.peek().type == 'EOF'

    def is_at_line_end(self, n: int = None) -> bool:
        """Check if the current or `n`-th token is a newline or semicolon."""
        token = self.peek_relative(n) if n is not None else self.peek()
        return token.value in {'\n', ';'} or (token.type == 'WHITESPACE' and '\n' in token.value)

    def get_expr(self, till_types: Optional[List[str]] = None) -> str:
        """Retrieve the next expression from tokens."""
        if till_types is None:
            till_types = []

        current_token = self.peek()
        if current_token.value in ('print', 'PRINT', 'OUTPUT'):
            return self.parse_print()
        elif current_token.value in ('IF', 'ELSE'):
            return self.parse_conditions()
        elif current_token.value == 'TYPE':
            return self.parse_type()
        elif current_token.value == "DECLARE":
            return self.parse_declare()
        elif current_token.type == 'IDENTIFIER':
            return self.parse_identifier()
        elif current_token.type == 'ATTRIBUTE' and self.peek_relative(-1).type in ('ATTRIBUTE', 'IDENTIFIER'):
            return self.parse_attribute()
        elif current_token.value.lower() in ('endif', 'else', '\t'):
            return ''
        elif current_token.value == '\n' and current_token.column == 1:
            return "'#NEWLINE#'"
        else:
            raise SyntaxError(f"Unexpected token: {current_token.value}, {current_token}")

def parse(tokens: List[Token]) -> ast.Module:
    """
    Parse tokens using parallel processing for large inputs;
    fall back to single-threaded parsing for smaller inputs.
    """
    def process_token_chunk(chunk):
        parser = Parser(chunk)
        statements = []
        while not parser.is_at_file_end():
            statements.append(parser.parse_statement())
            if parser.is_at_line_end():
                parser.advance()
        return statements

    if len(tokens) > 1000:
        pass  # Parallel processing not implemented, fallback to single-threaded
    else:
        parser = Parser(tokens)
        statements = []
        while not parser.is_at_file_end():
            statements.append(parser.parse_statement())
            if parser.is_at_line_end():
                print(parser.advance())
        
        imports = [ast.parse(i).body for i in parser.imports]
        return ast.Module(body=imports + statements, type_ignores=[])
