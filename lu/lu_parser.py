from typing import List, Optional
from lu_token import Token
import ast
from lu_errors import SyntaxError, NameError, RuntimeError
from expr import Expr
from TYPE import keyword_type
from elements import elements

class Parser(Expr,keyword_type,elements):
    def __init__(self, tokens: List[Token]) -> None:
        self.imports = []
        self.datatypes = ["INTEGER", "CHAR", "STRING", "DATE", "REAL","BOOLEAN"]
        self.tokens = tokens
        self.current = 0
        self.indent = 0

    def parse_statement(self) -> ast.AST:
        """Parse a single statement."""
        return ast.parse(self.get_expr()).body

    def peek(self) -> Token:
        """Returns the current token that is being parsed."""
        return self.tokens[self.current]

    def peek_relative(self, n: int) -> Token:
        """Returns the relative token to the current token being parsed."""
        k = self.current + n
        if k < 0 or k >= len(self.tokens):
            SyntaxError(f"List index out of range: {k}")
            return Token(type="EOF", value="", line=self.tokens[-1].line)
        return self.tokens[k]

    def advance(self) -> Token:
        """Increment/Consume current token index and return the previous token."""
        if self.is_at_file_end():
            return self.peek()  # Do not advance if EOF, return current EOF token
        self.current += 1
        if self.current >= len(self.tokens):  # Guard to prevent incrementing past end
            return self.tokens[-1]  # Return the last token (likely EOF) to avoid error
        return self.tokens[self.current - 1]

    def is_at_file_end(self, n: int = None) -> bool:
        """Checks for End Of File."""
        return self.peek().type == 'EOF' if n is None else self.peek_relative(n).type == 'EOF'
    
    def is_at_line_end(self, n: int = None) -> bool:
        """
        Checks if the current token or the token `n` positions ahead is a newline.
        Includes support for semicolon as line terminator.
        """
        token = self.peek_relative(n) if n is not None else self.peek()

        # Check if token is a newline or semicolon, but ignore TAB tokens
        return token.value == '\n' or token.value == ';' or token.type == 'WHITESPACE' and '\n' in token.value


    def get_expr(self, till_types: Optional[List[str]] = None) -> str:
        """Gets the next expression from the tokens."""
        if till_types is None:
            till_types = []

        # Initialize indentation
        # self.calculate_indentation()
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
        elif current_token.value.lower() in ('endif', 'else','\t'):
            return ''
        else:
            raise SyntaxError(f"Unexpected token: {current_token.value}, {current_token}")
    
    
    # def calculate_indentation(self) -> int:
    #     """Calculates the current indentation level based on TAB tokens."""
    #     token = self.peek()
    #     if token.type == 'TAB' and token.column == 1:
    #         indent_level = 1
    #         while self.peek_relative(1).value == '\t':
    #             indent_level += 1
    #             self.advance()  # Move past the TAB token
    #         self.advance()
    #         self.indent = indent_level

def parse(tokens: List[Token]) -> ast.Module:
    """
    Parse tokens using parallel processing for large inputs,
    fall back to single-threaded parsing for small inputs.
    """
    def process_token_chunk(chunk):
        parser = Parser(chunk)
        statements = []
        while not parser.is_at_file_end():
            statements.append(parser.parse_statement())
            if parser.is_at_line_end():
                parser.advance()
        return statements

    if len(tokens) > 1000:  # Large input, use parallel processing
        # Placeholder for multiprocessing logic (commented out for now)
        # num_chunks = 4  # Number of parallel processes
        # chunk_size = len(tokens) // num_chunks
        # chunks = [tokens[i:i+chunk_size] for i in range(0, len(tokens), chunk_size)]
        #
        # with Pool(num_chunks) as p:
        #     parsed_chunks = p.map(process_token_chunk, chunks)
        # statements = [stmt for chunk in parsed_chunks for stmt in chunk]
        pass  # Parallel processing not implemented, fallback to single-threaded

    else:
        parser = Parser(tokens)
        statements = []
        while not parser.is_at_file_end():
            statements.append(parser.parse_statement())
            if parser.is_at_line_end():
                parser.advance()
        imports = []
        for i in parser.imports:
            imports.append(ast.parse(i).body)
        statements = imports + statements
        return ast.Module(body=statements, type_ignores=[])
