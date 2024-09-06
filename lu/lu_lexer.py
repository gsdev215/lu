import re
from lu_token import Token

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.token_specs = [
            ('WHITESPACE', r'[\t\n]+'),
            ('SPACE', r'[ ]+'),  # Spaces are handled separately
            ('COMMENT', r'//.*'), 
            ('KEYWORD', r'\b(INPUT|OUTPUT|PRINT|print|IF|THEN|ELSE|ENDIF|WHILE|ENDWHILE|FOR|TO|STEP|NEXT|FUNCTION|ENDFUNCTION|RETURN|CALL|DECLARE|CONSTANT|TRUE|FALSE)\b'),  # Keywords and Boolean values
            ('IDENTIFIER', r'[a-zA-Z_]\w*'),
            ('ATTRIBUTE', r'\.[a-zA-Z_]\w*'),  # Attributes starting with a dot
            ('FUNCTION_CALL', r'[a-zA-Z_]\w*\(\)'),  # Function calls with parentheses
            ('CHAR', r"'.'"),  # Single character enclosed in single quotes
            ('STRING', r'"[^"]*"'),  # Zero or more characters enclosed in double quotes
            ('INTEGER', r'\b\d+\b'),  
            ('REAL', r'\b\d+\.\d+\b'),  # Numbers with decimal points
            ('BOOLEAN', r'\b(TRUE|FALSE)\b'),
            ('OPERATOR', r'(<-|->|\+|-|\*{1,2}|/|\^|=|<>|<|<=|>|>=)'),  # Operators: including `^` (power) and `<>` (not equal)
            ('DELIMITER', r'[\(\)\[\]\{\},;:]'),
        ] # you should agree AI are sometimes really usefull 

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
