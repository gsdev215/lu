import re
from lu_token import Token # Implementing AST

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.token_specs = [
            ('WHITESPACE', r'[\t\n]+'),
            ('COMMENT', r'//.*'),
            ('KEYWORD', r'\b(Declare|as|let|print|delete|del|if|else|while|for|func|return|pass|continue|end)\b'),
            ('IDENTIFIER', r'[a-zA-Z_]\w*'), 
            ('ATTRIBUTE', r'\.[a-zA-Z_]\w*'), 
            ('FUNCTION_CALL', r'\.[a-zA-Z_]\w*\(\)'), 
            ('NUMBER', r'\d+(\.\d+)?'),
            ('STRING', r'"[^"]*"'),
            ('OPERATOR', r'(\+|->|-|\*|/|==|!=|<|>|<=|>=|=)'),
            ('DELIMITER', r'[\(\)\[\]\{\},;:]'),
            ('SPACE', r'[ ]+'),
        ]
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        self.compiled_regex = re.compile(self.token_regex)

    def tokenize(self):
        tokens = []
        for match in self.compiled_regex.finditer(self.text):
            token_type = match.lastgroup
            value = match.group(token_type)
            if token_type in {'WHITESPACE', 'COMMENT', 'SPACE'}:
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
            # If there are newlines, reset the column to the length after the last newline
            self.column = len(value.rsplit('\n', 1)[-1]) + 1
        else:
            # If no newlines, just increment the column by the length of the value
            self.column += len(value)

        # Update the overall position in the text
        self.pos += len(value)

def tokenize_text(text: str):
    lexer = Lexer(text)
    return lexer.tokenize()
