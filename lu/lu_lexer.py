import re
from typing import List, NamedTuple

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.text):
            if token := self.match_whitespace():
                pass  # Ignore whitespace, but update position
            elif token := self.match_comment():
                tokens.append(token)
            elif token := self.match_keyword():
                tokens.append(token)
            elif token := self.match_identifier():
                tokens.append(token)
            elif token := self.match_number():
                tokens.append(token)
            elif token := self.match_string():
                tokens.append(token)
            elif token := self.match_operator():
                tokens.append(token)
            elif token := self.match_delimiter():
                tokens.append(token)
            else:
                raise SyntaxError(f"Unexpected character at line {self.line}, column {self.column}")
        
        tokens.append(Token('EOF', '', self.line, self.column))
        return tokens

    def match_pattern(self, pattern, token_type):
        match = re.match(pattern, self.text[self.pos:])
        if match:
            value = match.group()
            token = Token(token_type, value, self.line, self.column)
            self.advance(len(value))
            return token
        return None

    def match_whitespace(self):
        return self.match_pattern(r'\s+', 'WHITESPACE')

    def match_comment(self):
        return self.match_pattern(r'//.*', 'COMMENT')

    def match_keyword(self):
        keywords = r'\b(Declare|as|let|print|delete|del|if|else|while|for|function|return)\b'
        return self.match_pattern(keywords, 'KEYWORD')

    def match_identifier(self):
        return self.match_pattern(r'[a-zA-Z_]\w*', 'IDENTIFIER')

    def match_number(self):
        return self.match_pattern(r'\d+(\.\d+)?', 'NUMBER')

    def match_string(self):
        return self.match_pattern(r'"[^"]*"', 'STRING')

    def match_operator(self):
        operators = r'(\+|-|\*|/|==|!=|<|>|<=|>=|=)'
        return self.match_pattern(operators, 'OPERATOR')

    def match_delimiter(self):
        delimiters = r'[\(\)\[\]\{\},;:]'
        return self.match_pattern(delimiters, 'DELIMITER')

    def advance(self, length):
        lines = self.text[self.pos:self.pos+length].split('\n')
        if len(lines) > 1:
            self.line += len(lines) - 1
            self.column = len(lines[-1]) + 1
        else:
            self.column += length
        self.pos += length

def tokenize_text(text: str) -> List[Token]:
    lexer = Lexer(text)
    return lexer.tokenize()

# Example usage
#if __name__ == "__main__":
    sample_code = """
    Declare x as int
    let x = 5 + 3
    
    // This is a comment
    Declare message as string
    let message = "Hello, world!"
    
    print x
    print message
    
    delete x
    """
    
    """tokens = tokenize_text(sample_code)
    for token in tokens:
        print(token)"""