from typing import Tuple, Optional, List
from lu_errors import SyntaxError

class Expr:
    def parse_conditions(self) -> str:
        condition = self.advance().value.lower()
        if condition in ('if','else','elif','else if'):
            return self.parse_if_else(condition)

    def parse_if_else(self,keyword):
        indent_ = self.indent
        if keyword in ('if','elif','else if'):
            head=('    ' * self.indent) + keyword +' '
            condition = []
            while not self.is_at_line_end():
                condition.append(self.advance().value)
            head+= ''.join(condition) + ':\n'
            self.advance() # next line
        elif keyword == 'else':
            head= ('    ' * self.indent) + keyword + ':\n'
            self.advance()  # Move to the next line after ELSE
        else:
            raise SyntaxError(f"Expected 'IF' or 'ELSE', but got '{keyword}'")
        
        body = []
        self.indent += 1

        while not self.is_at_file_end():
            if self.peek().value.lower() == 'endif':
                self.advance() # consume endif
                break

            expr = self.get_expr()
            if expr is None:
                raise SyntaxError("Unexpected token or empty expression in the block.")
            elif expr == '':
                continue
            
            if expr.startswith('    ' * self.indent):
                body.append(expr + '\n')
            else:
                body.append(('    ' * self.indent) + expr + '\n')
            
            if self.is_at_line_end():
                self.advance()

            if self.peek().value.lower() == 'else':
                self.indent -= 1
                self.advance()
                body.append(self.parse_if_else('else'))
                break

        self.indent = indent_  # Reset indent to original level
        return head + ''.join(body)


    def parse_print(self) -> str:
        self.advance()
        print_args = self.collect_arguments()
        return f"print({print_args})"

    def parse_identifier(self) -> str:
        identifier = self.advance().value

        if self.peek().value == "(":
            args = self.collect_arguments()
            return f"{identifier}({args})"
        elif self.peek().value in ("<-", "="):
            self.advance()
            value_expr = []
            while not self.is_at_line_end():
                value_expr.append(self.advance().value)
            value_expr =  ''.join(value_expr)

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
        if self.peek_relative(-1).value == '(':
            paren_count = 1
            self.advance()  # Skip the opening parenthesis
        else:
            while not (self.is_at_line_end() or self.is_at_file_end()):
                paren_count = 0
                args.append(self.advance().value)
            else:
                args.append("\n")
                

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
