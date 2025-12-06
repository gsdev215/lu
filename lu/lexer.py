import re
from enum import Enum, auto
from typing import NamedTuple


class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int


class TokenType(Enum):
    # Special
    EOF = auto()
    NEWLINE = auto()
    WHITESPACE = auto()
    COMMENT = auto()

    # Literals
    INTEGER = auto()
    REAL = auto()
    STRING = auto()
    CHAR = auto()
    BOOLEAN = auto()

    # Identifiers
    IDENTIFIER = auto()
    ATTRIBUTE = auto()

    # Keywords
    KEYWORD = auto()

    # Operators
    OPERATOR = auto()

    # Delimiters
    DELIMITER = auto()


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.line = 1
        self.column = 1

        self.token_specs = [
            # NEWLINE and whitespace
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t\r]+'),

            # Comments
            ('COMMENT', r'//[^\n]*'),

            # Keywords
            ('KEYWORD', r'\b(INPUT|OUTPUT|PRINT|IF|THEN|ELSE|ENDIF|WHILE|ENDWHILE|FOR|TO|STEP|NEXT|FUNCTION|ENDFUNCTION|RETURN|CALL|DECLARE|CONSTANT|LET|DO|REPEAT|UNTIL|CASE|ENDCASE|SWITCH|ENDSWITCH)\b'),

            # Boolean literal
            ('BOOLEAN', r'\b(TRUE|FALSE)\b'),

            # Identifiers
            ('ATTRIBUTE', r'\.[a-zA-Z_]\w*'),
            ('IDENTIFIER', r'[a-zA-Z_]\w*'),

            # Literals
            ('CHAR', r"'.'"),
            ('STRING', r'"[^"]*"'),
            ('REAL', r'\b\d+\.\d+\b'),
            ('INTEGER', r'\b\d+\b'),

            # Operators (ordered by longest first)
            ('OPERATOR', r'(<<|>>|<=|>=|<>|==|!=|\*\*|<-|->|=|\+|-|\*|/|%|\^|<|>)'),

            # Delimiters
            ('DELIMITER', r'[()\[\]{},;:]'),
        ]

        self.token_regex = '|'.join(
            f'(?P<{name}>{pattern})' for name, pattern in self.token_specs
        )
        self.compiled = re.compile(self.token_regex)

    def tokenize(self):
        tokens = []

        for match in self.compiled.finditer(self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == 'WHITESPACE' or kind == 'COMMENT':
                self.update_position(value)
                continue

            tok = Token(kind, value, self.line, self.column) # type: ignore
            tokens.append(tok)
            self.update_position(value)

        tokens.append(Token('EOF', '', self.line, self.column))
        return tokens

    def update_position(self, text: str):
        if '\n' in text:
            self.line += text.count('\n')
            self.column = 1
        else:
            self.column += len(text)
