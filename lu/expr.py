from typing import Tuple, Optional, List
from lu_errors import SyntaxError

class Expr:

    def parse_print(self) -> str:
        """Parses a print statement and returns the print statement as a string."""
        self.advance()  # Consume print/PRINT/OUTPUT
        print_args = self.collect_arguments()
        print(print_args)
        return f"print({print_args})"

    def parse_identifier(self) -> str:
        """Parses identifiers, function calls, and variable assignments."""
        identifier = self.advance().value  # Consume the identifier

        if self.peek().value == "(":  # Function call
            args = self.collect_arguments()
            return f"{identifier}({args})"
        elif self.peek().value in ("<-", "="):
            self.advance()  # Consume the assignment operator
            value_expr = self.get_expr()
            return f"{identifier} = {value_expr}"
        elif self.peek().type == 'ATTRIBUTE': 
            return identifier+self.parse_attribute()
        else:
            return identifier

    def parse_attribute(self) -> str:
        """Parses attribute access and method calls on objects."""
        attribute_chain = self.advance().value  # Consume the first part of the attribute chain

        while self.peek().type == 'ATTRIBUTE':  # Continue parsing the attribute chain
            attribute_chain += self.advance().value

        if self.peek().value == "(":  
            args = self.collect_arguments()
            return f"{attribute_chain}({args})"
        else:
            return attribute_chain

    def collect_arguments(self) -> str:
        """Collects and returns function/method arguments as a string."""
        args = []
        paren_count = 1
        self.advance()  # Skip the opening parenthesis

        while paren_count > 0:
            if self.is_at_file_end():
                raise SyntaxError("Unexpected end of file: Function call does not have a closing parenthesis")
            
            if self.is_at_line_end():
                args.append('\n')
                self.advance()
                continue

            current_token = self.peek()
            
            if current_token.value == '(':
                paren_count += 1
            elif current_token.value == ')':
                paren_count -= 1
                if paren_count == 0:
                    break  # Don't include the final closing parenthesis

            args.append(current_token.value)
            self.advance()

        if paren_count > 0:
            raise SyntaxError("Function call does not have a closing parenthesis")

        self.advance()  # Skip the closing parenthesis
        return ''.join(args).strip()