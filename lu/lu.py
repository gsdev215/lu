import re
import ast
from typing import List, Dict, Any, Union

class LuError(Exception):
    pass

class Lu:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pytokens: List[str] = []
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.current_index = 0
        self.line_number = 1

    def compile(self) -> List[str]:
        while self.current_index < len(self.tokens):
            self.process_token()
        return self.pytokens

    def process_token(self):
        token = self.current_token.strip()
        
        if token == '/':
            self.handle_comment()
        elif token == 'print':
            self.handle_print()
        elif token == 'Declare':
            self.handle_declaration()
        elif token == 'let':
            self.handle_assignment()
        elif token == '\n':
            self.line_number += 1
            self.advance()
        else:
            self.advance()

    def handle_comment(self):
        while self.current_index < len(self.tokens) and self.current_token != '\n':
            self.advance()

    def handle_print(self):
        self.advance()
        expression = self.get_expression()
        self.pytokens.append(f'print(f"{expression}")\n')

    def handle_declaration(self):
        self.advance(2)  # Skip 'Declare' and space
        var_name = self.current_token
        self.advance(4)  # Skip variable name, 'as', space, and reach type
        var_type = self.current_token
        self.memory[var_name] = {"type": var_type, "value": None}
        self.advance()

    def handle_assignment(self):
        self.advance(2)  # Skip 'let' and space
        var_name = self.current_token
        if var_name not in self.memory:
            self.raise_error(f"Undefined variable: {var_name}")
        
        self.advance(4)  # Skip variable name, '=', and spaces
        expression = self.get_expression()
        value = self.evaluate_expression(expression)
        
        if not self.type_check(self.memory[var_name]["type"], value):
            self.raise_error(f"Type mismatch for variable {var_name}")
        
        self.memory[var_name]["value"] = value
        self.pytokens.append(f"{var_name} = {value}\n")

    def get_expression(self) -> str:
        expression = []
        while self.current_index < len(self.tokens) and self.current_token not in ('\n', 'EOF'):
            expression.append(self.current_token)
            self.advance()
        return ''.join(expression).strip()

    def evaluate_expression(self, expression: str) -> Union[int, float, str]:
        try:
            if self.is_arithmetic_expression(expression):
                return eval(expression)  # Note: eval is used for simplicity, but it's not safe for untrusted input
            else:
                result = ast.literal_eval(expression)
                return f'"{result}"' if isinstance(result, str) else result
        except (ValueError, SyntaxError):
            return f'"{expression}"'

    @staticmethod
    def is_arithmetic_expression(expression: str) -> bool:
        return bool(re.match(r'^[\d\+\-\*/\(\) ]+$', expression))

    def type_check(self, expected_type: str, value: Any) -> bool:
        if expected_type == "int":
            return isinstance(value, int)
        elif expected_type == "float":
            return isinstance(value, (int, float))
        elif expected_type == "string":
            return isinstance(value, str)
        return True  # Default case, can be expanded for more types

    def raise_error(self, message: str):
        raise LuError(f"Error on line {self.line_number}: {message}")

    @property
    def current_token(self) -> str:
        return self.tokens[self.current_index]

    def advance(self, steps: int = 1):
        self.current_index += steps

def tokenize_text(text: str) -> List[str]:
    return re.findall(r'\S+|\s+', text)

def process_file(input_filename: str, output_filename: str):
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            tokens = tokenize_text(infile.read())
        
        tokens.append("EOF")
        lu_instance = Lu(tokens)
        py_tokens = lu_instance.compile()
        
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.writelines(py_tokens)
        
        print(f"Compilation successful. Output written to {output_filename}")
    except LuError as e:
        print(f"Compilation failed: {str(e)}")
    except IOError as e:
        print(f"File error: {str(e)}")

if __name__ == "__main__":
    input_file = 'lu/lu/example.lumin'
    output_file = 'output.py'
    process_file(input_file, output_file)