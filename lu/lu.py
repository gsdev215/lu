import re

class Lu:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pytokens = []
        self.current_index = 0
        self.process_tokens()
    
    def luprint(self, message):
        self.pytokens.append(f'print(f"{message}")\n')
    
    def process_tokens(self):
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            
            if token.strip() == '/':
                self.handle_comment()
            elif token.strip() == 'print':
                self.handle_print()
            else:
                self.current_index += 1
    
    def handle_comment(self):
        self.current_index += 1
        while self.current_index < len(self.tokens) and self.tokens[self.current_index] != '\n':
            self.current_index += 1
    
    def handle_print(self):
        self.current_index += 1
        message = []
        while self.current_index < len(self.tokens) and self.tokens[self.current_index] not in ('\n', 'EOF'):
            message.append(self.tokens[self.current_index])
            self.current_index += 1
        self.luprint(''.join(message).strip())

def tokenize_text(text):
    """Tokenize the text based on spaces, tabs, newlines, and indentation."""
    tokens = re.findall(r'\S+|\s+', text)
    return tokens

def process_file(input_filename, output_filename):
    """Read text from input file, tokenize it, and write tokens to output file."""
    with open(input_filename, 'r', encoding='utf-8') as infile, \
         open(output_filename, 'w', encoding='utf-8') as outfile:
            tokens = tokenize_text(infile.read())
            tokens.append("EOF")
            lu_instance = Lu(tokens)
            outfile.write(''.join(lu_instance.pytokens))

if __name__ == "__main__":
    input_file = '~/example.lumin'  # Replace with your input file name
    output_file = 'output.py'  # Replace with your output file name
    process_file(input_file, output_file)