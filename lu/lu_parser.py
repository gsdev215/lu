from typing import List, Any, Optional , Tuple
from lu_token import Token
import ast
from lu_errors import SyntaxError, Error
from expr import expr


class Parser(expr):
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.indent = 0

    def parse_statement(self) -> ast.AST:
        """Parse a single statement."""
        return self.get_expr()

    def peek(self) -> Token:
        """Returns the current token that is being parsed."""
        return self.tokens[self.current]

    def peek_relative(self, n: int) -> Token:
        """Returns the relative token to the current token being parsed."""
        if (k := self.current + n) <= len(self.tokens) - 1:
            return self.tokens[k]
        raise SyntaxError(f"List index out of range: {k}")

    def advance(self) -> Token:
        """Increment/Consumes current token index and return the previous token."""
        if self.is_at_file_end():
            return self.peek()
        self.current += 1
        return self.tokens[self.current - 1]

    def is_at_file_end(self, n: int = None) -> bool:
        """Checks for End Of File"""
        return self.peek().type == 'EOF' if n is None else self.peek_relative(n).type == 'EOF'
    
    def is_at_line_end(self, n: int = None) -> bool:
        """Checks if the current token or the token `n` positions ahead is a newline.
        """
        token = self.peek_relative(n) if n is not None else self.peek()
        return token.value == '\n'
    

    def get_expr(self, till_types: Optional[List[str]] = None) -> Tuple[List[ast.AST], List[ast.keyword]]:
        if till_types is None:
            till_types = []

        token_type = self.peek().type

        if token_type == 'FUNCTION_CALL':
            return self.parse_function_call()

        elif self.peek().value in ('print', 'PRINT', 'OUTPUT'):
            return self.parse_print()

        elif token_type == 'IDENTIFIER':
            return self.parse_identifier()

        elif token_type == 'ATTRIBUTE' and self.peek_relative(-1).type in ('ATTRIBUTE', 'IDENTIFIER'):
            return self.parse_attribute()

        else:
            SyntaxError(f"Unexpected token: {self.peek().value}")

def parse(tokens: List[Token]) -> ast.Module:
    """
    Parse tokens using parallel processing for large inputs,
    fall back to single-threaded parsing for small inputs.
    """
    if len(tokens) > 1000:  # Arbitrary threshold, adjust as needed
        return parse(tokens) #TODO
    else:
        parser = Parser(tokens)
        statements = []
        while not parser.is_at_file_end():
            statements.append(parser.parse_statement())
            if parser.is_at_line_end():
                parser.advance()
        return ast.Module(body=statements, type_ignores=[])
