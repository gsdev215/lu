from typing import List, Dict, Any, Union
from lu_errors import Error, SyntaxError, TypeError, NameError
from lu_functions import FunctionManager, LuFunction
from lu_lexer import Token
from lu_logger import debug, info, error
import ast

class Lu:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pytokens: List[str] = []
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.current_index = 0
        self.function_manager = FunctionManager()

    def compile(self) -> List[str]:
        info("Starting compilation process")
        while self.current_token.type != 'EOF':
            try:
                self.process_statement()
            except Error as e:
                error(f"Error during compilation: {e.full_message}")
                raise
        info("Compilation process completed")
        return self.pytokens

    def process_statement(self):
        if self.current_token.type == 'KEYWORD':
            if self.current_token.value == 'Declare':
                self.handle_declaration()
            elif self.current_token.value == 'let':
                self.handle_assignment()
            elif self.current_token.value in ('delete', 'del'):
                self.handle_deletion()
            elif self.current_token.value == 'print':
                self.handle_print()
            elif self.current_token.value == 'function':
                self.handle_function_definition()
            elif self.current_token.value == 'return':
                self.handle_return_statement()
            else:
                self.raise_error(SyntaxError, f"Unexpected keyword: {self.current_token.value}", expected="Declare, let, delete, del, or print")
        elif self.current_token.type == 'COMMENT':
            self.handle_comment()
        else:
            self.raise_error(SyntaxError, f"Unexpected token: {self.current_token.value}")

    def handle_comment(self):
        self.pytokens.append(f"# {self.current_token.value[2:]}\n")
        self.advance()

    def handle_print(self):
        self.advance()  # Skip 'print'
        expression = self.get_expression()
        self.pytokens.append(f'print({expression})\n')

    def handle_declaration(self):
        self.advance()  # Skip 'Declare'
        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected identifier after 'Declare'")
        var_name = self.current_token.value
        self.advance()

        if self.current_token.value != 'as':
            self.raise_error(SyntaxError, "Expected 'as' after variable name in declaration")
        self.advance()

        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected type after 'as' in declaration")
        var_type = self.current_token.value
        self.advance()

        self.memory[var_name] = {"type": var_type, "value": None}

    def handle_assignment(self):
        self.advance()  # Skip 'let'
        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected identifier after 'let'")
        var_name = self.current_token.value
        if var_name not in self.memory:
            self.raise_error(NameError, f"Undefined variable: {var_name}")
        self.advance()

        if self.current_token.value != '=':
            self.raise_error(SyntaxError, "Expected '=' in assignment")
        self.advance()

        expression = self.get_expression()
        if not self.type_check(self.memory[var_name]["type"], expression):
            self.raise_error(TypeError, f"Type mismatch for variable {var_name}")
        
        self.memory[var_name]["value"] = expression
        self.pytokens.append(f"{var_name} = {expression}\n")

    def handle_deletion(self):
        self.advance()  # Skip 'delete' or 'del'
        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected identifier after 'delete' or 'del'")
        var_name = self.current_token.value
        if var_name not in self.memory:
            self.raise_error(NameError, f"Cannot delete undefined variable: {var_name}")
        
        del self.memory[var_name]
        self.pytokens.append(f"del {var_name}\n")
        self.advance()

    def handle_function_definition(self):
        self.advance()  # Skip 'function'
        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected function name after 'function'")
        function_name = self.current_token.value
        self.advance()

        parameters = self.parse_function_parameters()
        return_type = self.parse_return_type()
        body = self.parse_function_body()

        function = LuFunction(function_name, parameters, return_type, body)
        self.function_manager.define_function(function)
        self.pytokens.extend(self.function_manager.compile_function(function))

    def parse_function_parameters(self):
        # TODO
        pass

    def parse_return_type(self):
        # TODO
        pass

    def parse_function_body(self):
        # TODO
        pass

    def handle_return_statement(self):
        # TODO
        pass

    def get_expression(self) -> str:
        expression = []
        current_line = self.current_token.line
        while self.current_token.type not in ('EOF', 'COMMENT'):
            if self.current_token.line != current_line:
                break
            expression.append(self.current_token.value)
            self.advance()
        return ' '.join(expression)

    def type_check(self, expected_type: str, value: str) -> bool:
        try:
            evaluated = ast.literal_eval(value)
            if expected_type == "int":
                return isinstance(evaluated, int)
            elif expected_type in ("float", "double"):
                return isinstance(evaluated, (int, float))
            elif expected_type in ("string","str"):
                return isinstance(evaluated, str)
            elif expected_type == "list":
                return isinstance(evaluated, list)
            elif expected_type == "tuple":
                return isinstance(evaluated, tuple)
            elif expected_type == "dict":
                return isinstance(evaluated, dict)
        except (ValueError, SyntaxError):
            # If literal_eval fails, it might be an arithmetic expression
            if expected_type in ("int", "float", "double"):
                return self.is_arithmetic_expression(value)
        return False

    @staticmethod
    def is_arithmetic_expression(expression: str) -> bool:
        try:
            ast.parse(expression, mode='eval')
            return True
        except SyntaxError:
            return False

    def raise_error(self, error_class: type, message: str, **kwargs):
        debug(f"Raising error: {error_class.__name__} - {message}")
        raise error_class(message, self.current_token, **kwargs)

    @property
    def current_token(self) -> Token:
        return self.tokens[self.current_index]

    def advance(self):
        self.current_index += 1
        debug(f"Advanced to token: {self.current_token}")