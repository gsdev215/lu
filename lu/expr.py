import ast
from typing import Tuple , Optional , List
from lu_errors import SyntaxError

class expr:

    def parse_function_call(self):
        """Parses a function call."""
        func_name = self.advance().value  # Consume the function name
        try:
            return ast.parse(f"{func_name}").body
        except Exception as e:
            SyntaxError(f"Invalid function call syntax: {e}")

    def parse_print(self):
        """Parses a print statement."""
        value = self.advance().value  # Consume print/PRINT/OUTPUT
        print_args = self.collect_arguments()
        value = f"print({print_args})"

        try:
            return ast.parse(value).body
        except Exception as e:
            SyntaxError(f"Error in parsing print statement: {e}")

    def parse_identifier(self):
        """Parses identifiers and function calls starting with an identifier."""
        identifier = self.advance().value  # Consume the identifier
        if self.peek().value == "(":
            args = self.collect_arguments()
            try:
                return ast.parse(f"{identifier}({args})").body
            except Exception as e:
                SyntaxError(f"Error in function call for '{identifier}': {e}")
        else:
            return ast.parse(identifier).body

    def parse_attribute(self):
        """Parses attribute access and method calls on objects."""
        attribute_chain = self.advance().value  # Start with the first attribute

        while self.peek().type == 'ATTRIBUTE':
            attribute_chain += self.advance().value  # Consume the next part of the attribute chain

        if self.peek().value == "(":
            args = self.collect_arguments()
            try:
                return ast.parse(f"{attribute_chain}({args})").body
            except Exception as e:
                SyntaxError(f"Error in method call '{attribute_chain}': {e}")
        else:
            try:
                return ast.parse(attribute_chain).body
            except Exception as e:
                SyntaxError(f"Error in attribute access '{attribute_chain}': {e}")

    def collect_arguments(self) -> str:
        """Collects and returns function/method arguments as a string."""
        args = []
        self.advance()  # Skip the opening parenthesis
        while self.peek().value != ")":
            if self.is_at_line_end() or self.is_at_file_end():
                SyntaxError("Function call does not have closing parenthesis")
                return
            args.append(self.advance().value)
        self.advance()  # Skip the closing parenthesis
        return ''.join(args)