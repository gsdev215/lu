from typing import List, Any, Optional , Tuple
from lu_token import Token
import ast
from lu_errors import SyntaxError, Error


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.indent = 0
        self.statements = []

    def peek(self) -> Token:
        """Returns the current token that is being parsed."""
        return self.tokens[self.current]

    def peek_relative(self, n: int) -> Token:
        """Returns the relative token to the current token being parsed."""
        if (k := self.current + n) <= len(self.tokens) - 1:
            return self.tokens[k]
        raise SyntaxError(f"List index out of range: {k}")

    def advance(self) -> Token:
        """Increment/Consumes current token index and return the previous token."""
        if self.is_at_end():
            return self.peek()
        self.current += 1
        return self.tokens[self.current - 1]

    def is_at_end(self, n: int = None) -> bool:
        """Checks for End Of File"""
        return self.peek().type == 'EOF' if n is None else self.peek_relative(n).type == 'EOF'

    def keywords(self):
        # TODO: Implement keyword handling
        pass

    def match(self, *types) -> bool:
        """Check if the current token matches any of the given types."""
        for type in types:
            if self.peek().type == type:
                return True
        return False


    def get_exp(self) -> Tuple[List[ast.AST], List[ast.keyword]]:
        args = []
        keywords = []
        expect_closing_paren = False

        # Check if the expression starts with an '('
        if self.peek().value == '(':
            self.advance()
            expect_closing_paren = True

        while not self.is_at_end():
            # Handle keywords
            if self.match('IDENTIFIER') and self.peek_relative(1).type == 'OPERATOR' and self.peek_relative(1).value == '=':
                keyword_name = self.advance().value
                self.advance()  
                keyword_value = self.get_term()
                keywords.append(ast.keyword(arg=keyword_name, value=keyword_value))
            else:
                expr = self.get_term()

                # Handle operations
                while self.match('OPERATOR') and not self.is_at_end():
                    op = self.advance()
                    right = self.get_term()

                    if op.value in ('and', 'or'):
                        expr = ast.BoolOp(
                            op=ast.And() if op.value == 'and' else ast.Or(),
                            values=[expr, right]
                        )
                    elif op.value in ('==', '!=', '<', '>', '<=', '>='):
                        expr = ast.Compare(
                            left=expr,
                            ops=[self.get_comparison_op(op.value)],
                            comparators=[right]
                        )
                    elif op.value in ('+', '-', '*', '/', '**'):
                        expr = ast.BinOp(
                            left=expr,
                            op=self.get_binary_op(op.value),
                            right=right
                        )
                    else:
                        raise SyntaxError(f"Unexpected operator: {op.value}")

                args.append(expr)

            # Check for delimiter
            if self.match('DELIMITER'):
                delim = self.advance()
                if delim.value == ',':
                    continue
                elif delim.value == ')':
                    if expect_closing_paren:
                        break
                    else:
                        raise SyntaxError("Unexpected closing parenthesis")
                else:
                    raise SyntaxError(f"Unexpected delimiter: {delim.value}")
            else:
                break

        if expect_closing_paren and self.peek().value != ')':
            raise SyntaxError("Expected closing parenthesis")

        return args, keywords

    def get_term(self) -> ast.AST:
        if self.match("STRING"):
            return ast.Constant(value=self.advance().value.strip('"'))
        elif self.match("NUMBER"):
            value = self.advance().value
            return ast.Constant(value=float(value) if '.' in value else int(value))
        elif self.match('IDENTIFIER'):
            return ast.Name(id=self.advance().value, ctx=ast.Load())
        elif self.match('OPERATOR') and self.peek().value in ('-', 'not'):
            op = self.advance()
            expr = self.get_term()
            return ast.UnaryOp(
                op=ast.USub() if op.value == '-' else ast.Not(),
                operand=expr
            )
        else:
            raise SyntaxError(f"Unexpected token: {self.peek().value}",self.peek())

    def get_comparison_op(self, op: str) -> ast.cmpop:
        return {
            '==': ast.Eq(),
            '!=': ast.NotEq(),
            '<': ast.Lt(),
            '>': ast.Gt(),
            '<=': ast.LtE(),
            '>=': ast.GtE()
        }[op]

    def get_binary_op(self, op: str) -> ast.operator:
        return {
            '+': ast.Add(),
            '-': ast.Sub(),
            '*': ast.Mult(),
            '/': ast.Div(),
            '**': ast.Pow()
        }[op]

    def print_handling(self):
        self.advance()  # Advance past 'print'
        args, keywords = self.get_exp()
        if not args:
            raise Error(f"Expected expression after 'print' at line {self.peek().line}")
        self.statements.append(ast.Expr(
            value=ast.Call(
                func=ast.Name(id='print', ctx=ast.Load()),
                args=args,
                keywords=keywords
            )
        ))

def parse(tokens):
    #TODO
    pass