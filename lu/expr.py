from typing import Tuple, Optional, List
from lu_errors import SyntaxError

class Expr:
    def parse_conditions(self) -> str:
        x = self.advance().value.lower()  # Consume IF
        args = ('    ' * self.indent) + x + ' '
        indent_level = self.indent
        condition = []

        while not self.is_at_line_end() and self.indent >= indent_level:
            while not self.is_at_line_end():
                condition.append(self.advance().value)
            else:
                self.calculate_indentation()

        args += ''.join(condition) + ':\n'
        self.advance()

        block = []
        self.indent += 1
        while self.indent > indent_level:
            expr = self.get_expr()
            if expr is None:
                SyntaxError("Unexpected token or empty expression in the block.")
            elif expr == '':
                self.indent -= 1
                return args + ''.join(block)
            block.append(('    ' * self.indent) + expr + '\n')
            self.calculate_indentation()
            if self.is_at_line_end():
                self.advance()
            if self.is_at_file_end():
                raise SyntaxError("Unexpected end of file, missing 'ENDIF'.")

        return args + ''.join(block)

    def parse_print(self) -> str:
        self.advance()
        print_args = self.collect_arguments()
        print(print_args)
        return f"print({print_args})"

    def parse_identifier(self) -> str:
        identifier = self.advance().value

        if self.peek().value == "(":
            args = self.collect_arguments()
            return f"{identifier}({args})"
        elif self.peek().value in ("<-", "="):
            self.advance()
            value_expr = self.get_expr()
            return f"{identifier} = {value_expr}"
        elif self.peek().type == 'ATTRIBUTE': 
            return identifier + self.parse_attribute()
        else:
            return identifier

    def parse_attribute(self) -> str:
        attribute_chain = self.advance().value

        while self.peek().type == 'ATTRIBUTE':
            attribute_chain += self.advance().value

        if self.peek().value == "(":
            args = self.collect_arguments()
            return f"{attribute_chain}({args})"
        else:
            return attribute_chain

    def collect_arguments(self) -> str:
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
                    break

            args.append(current_token.value)
            self.advance()

        if paren_count > 0:
            raise SyntaxError("Function call does not have a closing parenthesis")

        self.advance()  # Skip the closing parenthesis
        return ''.join(args).strip()
