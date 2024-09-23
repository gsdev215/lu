import re
from lu_token import Token

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.token_specs = [
            # Whitespace and Comments
            ('WHITESPACE', r'[\t\n]+'),  # Matches tabs and newlines
            ('SPACE', r'[ ]+'),          # Matches spaces
            ('COMMENT', r'//.*'),        # Single-line comments starting with //

            # Boolean and Logical Operators
            ('BOOLEAN', r'\b(TRUE|FALSE)\b'),  # Boolean literals TRUE, FALSE
            ('BOOLEANOP', r'\b(NOT OR|NOT AND|OR|AND|NOT)\b'),  # Logical operators AND, OR, NOT

            # Keywords
            ('KEYWORD', r'\b(INPUT|OUTPUT|PRINT|IF|THEN|ELSE|ENDIF|WHILE|ENDWHILE|FOR|TO|STEP|NEXT|FUNCTION|ENDFUNCTION|RETURN|CALL|DECLARE|CONSTANT|LET|DO|REPEAT|UNTIL|CASE|ENDCASE|SWITCH|ENDSWITCH|TRUE|FALSE)\b'),

            # Identifiers and Functions
            ('FUNCTION_CALL', r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(\s*((([A-Za-z_][A-Za-z0-9_]*|\".*?\"|'.*?'|\d+(\.\d+)?|\[.*?\]|\{.*?\}|\(.*?\))\s*(,\s*)?)*)\s*\)"),  # Function calls with parentheses (e.g., myFunction())
            ('IDENTIFIER', r'[a-zA-Z_]\w*'),  # Variable/function names (alphanumeric and underscores)
            ('ATTRIBUTE', r'\.[a-zA-Z_]\w*'),  # Attributes starting with a dot (e.g., object.property)

            # Character and String Literals
            ('CHAR', r"'.'"),  # Single characters enclosed in single quotes
            ('STRING', r'"[^"]*"'),  # Strings enclosed in double quotes

            # Numeric Literals
            ('INTEGER', r'\b\d+\b'),  # Integer literals (whole numbers)
            ('REAL', r'\b\d+\.\d+\b'),  # Real (floating point) numbers

            # Operators (Arithmetic, Assignment, Comparison, and Bitwise)
            ('OPERATOR', r'(<-|←|->|==|\+|-|\*{1,2}|/|\^|=|<>|<|<=|>|>=|%|&|\||\^|~|<<|>>)'),  # All operators

            # Delimiters
            ('DELIMITER', r'[\(\)\[\]\{\},;:]'),  # Parentheses, brackets, commas, etc.
        ]


        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        self.compiled_regex = re.compile(self.token_regex)

    def tokenize(self):
        tokens = []
        for match in self.compiled_regex.finditer(self.text):
            token_type = match.lastgroup
            value = match.group(token_type)
            if token_type in {'COMMENT', 'SPACE'}:
                self.update_position(value)
                continue
            else:
                token = Token(token_type, value, self.line, self.column)
                tokens.append(token)
                self.update_position(value)
        tokens.append(Token('EOF', '', self.line, self.column))
        return tokens

    def update_position(self, value: str):
        """Update line and column positions after processing a token."""
        newline_count = value.count('\n')
        semicolon_count = value.count(';')

        # Increment line number for each newline and semicolon
        self.line += newline_count + semicolon_count

        if newline_count > 0:
            self.column = len(value.rsplit('\n', 1)[-1]) + 1
        else:
            self.column += len(value)
        self.pos += len(value)

def tokenize_text(text: str):
    lexer = Lexer(text)
    return lexer.tokenize()
