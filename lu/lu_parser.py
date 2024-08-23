from typing import List, Dict, Any, Union
from lu_errors import Error, SyntaxError, TypeError, NameError, ArgumentError, ReturnError
from lu_functions import FunctionManager, LuFunction
from lu_lexer import Token
from lu_logger import debug, info, error
import ast

class Lu:
    """
    Main class for parsing and compiling Lu code into Python.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pytokens: List[str] = []
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.current_index = 0
        self.function_manager = FunctionManager()
        self.indent_level = 0
        self.in_function = False
        self.current_function: Union[LuFunction, None] = None

    def compile(self) -> List[str]:
        """
        Main compilation method. Processes all tokens and generates Python code.
        """
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
        """
        Process a single statement based on the current token.
        """
        if self.current_token.type == 'KEYWORD':
            self.handle_keyword()
        elif self.current_token.type == 'COMMENT':
            self.handle_comment()
        elif self.current_token.type == 'WHITESPACE':
            self.handle_whitespace()
        else:
            self.raise_error(SyntaxError, f"Unexpected token: {self.current_token.value}")

    def handle_keyword(self):
        """
        Handle different keywords and direct to appropriate methods.
        """
        keyword_handlers = {
            'Declare': self.handle_declaration,
            'let': self.handle_assignment,
            'delete': self.handle_deletion,
            'del': self.handle_deletion,
            'print': self.handle_print,
            'func': self.handle_function_definition,
            'return': self.handle_return_statement,
            'if': self.handle_if,
            'while': self.handle_while,
            'for': self.handle_for,
            'pass': self.handle_pass,
            'continue': self.handle_continue,
            'break': self.handle_break
        }
        handler = keyword_handlers.get(self.current_token.value)
        if handler:
            handler()
        else:
            self.raise_error(SyntaxError, f"Unexpected keyword: {self.current_token.value}")

    def handle_if(self):
        """
        Handle if-elif-else statements.
        """
        self.advance()  # Skip 'if'
        condition = self.get_expression()
        self.pytokens.append(f"{self.indent}if {condition}:\n")
        self.indent_level += 1
        self.parse_block()
        self.indent_level -= 1
        
        while self.current_token.value == 'else':
            self.advance()  # Skip 'else'
            if self.current_token.value == 'if':
                self.advance()  # Skip 'if'
                condition = self.get_expression()
                self.pytokens.append(f"{self.indent}elif {condition}:\n")
            else:
                self.pytokens.append(f"{self.indent}else:\n")
            self.indent_level += 1
            self.parse_block()
            self.indent_level -= 1

    def handle_while(self):
        """
        Handle while loops.
        """
        self.advance()  # Skip 'while'
        condition = self.get_expression()
        self.pytokens.append(f"{self.indent}while {condition}:\n")
        self.indent_level += 1
        self.parse_block()
        self.indent_level -= 1

    def handle_for(self):
        """
        Handle for loops.
        """
        self.advance()  # Skip 'for'
        iterator = self.current_token.value
        self.advance()
        if self.current_token.value != 'in':
            self.raise_error(SyntaxError, "Expected 'in' in for loop")
        self.advance()
        iterable = self.get_expression()
        self.pytokens.append(f"{self.indent}for {iterator} in {iterable}:\n")
        self.indent_level += 1
        self.parse_block()
        self.indent_level -= 1

    def parse_block(self):
        """
        Parse a block of code (function body, loop body, etc.)
        """
        while self.current_token.type != 'EOF':
            if self.current_token.type == 'WHITESPACE':
                self.handle_whitespace()
            elif self.current_token.type == 'KEYWORD' and self.current_token.value in ('else', 'elif'):
                break
            else:
                self.process_statement()

    def handle_pass(self):
        """
        Handle pass statement.
        """
        self.pytokens.append(f"{self.indent}pass")
        self.advance()

    def handle_continue(self):
        """
        Handle continue statement.
        """
        self.pytokens.append(f"{self.indent}continue")
        self.advance()

    def handle_break(self):
        """
        Handle break statement.
        """
        self.pytokens.append(f"{self.indent}break")
        self.advance()

    def handle_whitespace(self):
        """
        Handle whitespace, including newlines for proper indentation.
        """
        if '\n' in self.current_token.value:
            self.pytokens.append('\n')
        self.advance()

    def handle_comment(self):
        """
        Handle comments by converting them to Python comments.
        """
        self.pytokens.append(f"{self.indent}# {self.current_token.value[2:]}")
        self.advance()

    def handle_print(self):
        """
        Handle print statements.
        """
        self.advance()  # Skip 'print'
        expression = self.get_expression()
        self.pytokens.append(f'{self.indent}print({expression})')

    def handle_declaration(self):
        """
        Handle variable declarations.
        """
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
        """
        Handle variable assignments.
        """
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
        self.pytokens.append(f"{self.indent}{var_name} = {expression}")

    def handle_deletion(self):
        """
        Handle variable deletion.
        """
        self.advance()  # Skip 'delete' or 'del'
        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected identifier after 'delete' or 'del'")
        var_name = self.current_token.value
        if var_name not in self.memory:
            self.raise_error(NameError, f"Cannot delete undefined variable: {var_name}")
        
        del self.memory[var_name]
        self.pytokens.append(f"{self.indent}del {var_name}\n")
        self.advance()

    def handle_function_definition(self):
        """
        Handle function definitions.
        """
        self.advance()  # Skip 'func'
        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected function name after 'function'")
        function_name = self.current_token.value
        self.advance()

        parameters = self.parse_function_parameters()
        return_type = self.parse_return_type()
        
        self.in_function = True
        self.current_function = LuFunction(function_name, parameters, return_type, [])
        self.pytokens.append(f"{self.indent}def {function_name}({', '.join(param['name'] for param in parameters)}):\n")
        
        self.indent_level += 1
        self.parse_block()
        self.indent_level -= 1
        
        self.function_manager.define_function(self.current_function)
        self.in_function = False
        self.current_function = None

    def parse_function_parameters(self):
        """
        Parse function parameters.
        """
        parameters = []
        if self.current_token.value != '(':
            self.raise_error(SyntaxError, "Expected '(' after function name")
        self.advance()

        while self.current_token.value != ')':
            if self.current_token.type != 'IDENTIFIER':
                self.raise_error(SyntaxError, "Expected parameter name")
            param_name = self.current_token.value
            self.advance()

            if self.current_token.value != ':':
                self.raise_error(SyntaxError, "Expected ':' after parameter name")
            self.advance()

            if self.current_token.type != 'IDENTIFIER':
                self.raise_error(SyntaxError, "Expected parameter type")
            param_type = self.current_token.value
            self.advance()

            parameters.append({"name": param_name, "type": param_type})

            if self.current_token.value == ',':
                self.advance()
            elif self.current_token.value != ')':
                self.raise_error(SyntaxError, "Expected ',' or ')' after parameter")

        self.advance()  # Skip ')'
        return parameters

    def parse_return_type(self):
        """
        Parse function return type.
        """
        #if self.current_token.value != '->':
        #    self.raise_error(SyntaxError, "Expected '->' before return type")
        self.advance(2)# skip "->"

        if self.current_token.type != 'IDENTIFIER':
            self.raise_error(SyntaxError, "Expected return type")
        return_type = self.current_token.value
        self.advance()

        return return_type

    def handle_return_statement(self):
        """
        Handle return statements.
        """
        if not self.in_function:
            self.raise_error(SyntaxError, "Return statement outside function")
        
        self.advance()  # Skip 'return'
        expression = self.get_expression()
        
        if not self.type_check(self.current_function.return_type, expression):
            self.raise_error(TypeError, f"Return type mismatch. Expected {self.current_function.return_type}")
        
        self.pytokens.append(f"{self.indent}return {expression}\n")
        self.indent_level -= 1

    def get_expression(self) -> str:
        """
        Get a full expression from the current position.
        """
        expression = []
        current_line = self.current_token.line
        while self.current_token.type not in ('EOF', 'COMMENT','WHITESPACE'):
            if self.current_token.line != current_line:
                break
            expression.append(self.current_token.value)
            self.advance()
        return ' '.join(expression)

    def type_check(self, expected_type: str, value: str) -> bool:
        """
        Check if a value matches the expected type.
        """
        try:
            evaluated = ast.literal_eval(value)
            if expected_type == "int":
                return isinstance(evaluated, int)
            elif expected_type in ("float", "double"):
                return isinstance(evaluated, (int, float))
            elif expected_type in ("string", "str"):
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
        """
        Check if a string represents a valid arithmetic expression.
        """
        try:
            ast.parse(expression, mode='eval')
            return True
        except SyntaxError:
            return False

    def raise_error(self, error_class: type, message: str, **kwargs):
        """
        Raise a custom error with detailed information.
        """
        debug(f"Raising error: {error_class.__name__} - {message}")
        raise error_class(message, self.current_token, **kwargs)

    @property
    def current_token(self) -> Token:
        """
        Get the current token.
        """
        return self.tokens[self.current_index]

    def advance(self,n=1):
        """
        Move to the next token.
        """
        self.current_index += n
        debug(f"Advanced to token: {self.current_token}")

    @property
    def indent(self):
        """
        Get the current indentation string.
        """
        return '    ' * self.indent_level