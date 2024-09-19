from typing import List, Any, Optional , Tuple
from lu_token import Token
import ast
from lu_errors import SyntaxError, Error


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.indent = 0

    def parse_statement(self) -> ast.AST:
        """Parse a single statement."""
        if self.match('KEYWORD'):
            return self.keywords()
        elif self.match('IDENTIFIER'):
            return self.assignment()
        
        else:
            # Handle other types of statements (e.g., expressions)
            expr = self.get_exp()[0]
            return ast.Expr(value=expr)

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
        if self.is_at_file_end():
            return self.peek()
        self.current += 1
        return self.tokens[self.current - 1]

    def is_at_file_end(self, n: int = None) -> bool:
        """Checks for End Of File"""
        return self.peek().type == 'EOF' if n is None else self.peek_relative(n).type == 'EOF'
    
    def is_at_line_end(self, n: int = None) -> bool:
        """Checks if the current token or the token `n` positions ahead is a newline.
        """
        token = self.peek_relative(n) if n is not None else self.peek()
        return token.type == 'WHITESPACE' and token.value == '\n'
    

    def assignment(self) -> ast.AST:
        var_name = self.advance().value
        if self.advance().value not in ('<-', '='):
            raise SyntaxError("Expected '<-' or '=' in assignment")
        args, keywords = self.get_exp()
        if keywords:
            raise SyntaxError("Invalid syntax. Keyword arguments not allowed in assignment.")
        if len(args) == 1:
            value = args[0]
        elif len(args) > 1:
            value = ast.Tuple(elts=args, ctx=ast.Load())
        else:
            raise SyntaxError("No value provided for assignment")

        return ast.Assign(
            targets=[ast.Name(id=var_name, ctx=ast.Store())],
            value=value
        )

    def keywords(self) -> ast.AST:
        keyword = self.advance().value
        if keyword == 'INPUT':
            return self.input_handling()
        elif keyword in ('OUTPUT', 'PRINT', 'print'):
            return self.print_handling()
        elif keyword == 'IF':
            return self.if_handling()
        elif keyword == 'WHILE':
            return self.while_handling()
        elif keyword == 'FOR':
            return self.for_handling()
        elif keyword == 'FUNCTION':
            return self.function_handling()
        elif keyword == 'RETURN':
            return self.return_handling()
        elif keyword == 'CALL':
            return self.call_handling()
        elif keyword == 'DECLARE':
            return self.declare_handling()
        elif keyword == 'CONSTANT':
            return self.constant_handling()
        elif keyword == 'ENDIF':
            pass
        else:
            raise SyntaxError(f"Unexpected keyword: {keyword}")


    def match(self, *types) -> bool:
        """Check if the current token matches any of the given types."""
        for type in types:
            if self.peek().type == type:
                return True
        return False


    def get_exp(self, till_types: Optional[List[str]] = None) -> Tuple[List[ast.AST], List[ast.keyword]]:
        if till_types is None:
            till_types = []

        args = []
        keywords = []
        expect_closing_paren = False

        if self.match('KEYWORD'):
            self.advance()
        if self.peek().value == '(':
            self.advance()
            expect_closing_paren = True

        while not (self.is_at_line_end() or self.is_at_file_end()):
            # Handle keywords
            if self.peek().type in till_types:
                break
            if self.match('IDENTIFIER') and self.peek_relative(1).type == 'OPERATOR' and self.peek_relative(1).value in ('=', '<-', '←'):
                keyword_name = self.advance().value
                self.advance()
                keyword_value = self.get_term()
                keywords.append(ast.keyword(arg=keyword_name, value=keyword_value))
            elif self.match('DELIMITER') and not self.peek_relative(-1).type == 'KEYWORD':
                delim = self.advance()
                if delim.value == ',':
                    continue
                elif delim.value == ')':
                    if expect_closing_paren:
                        break
                    else:
                        raise SyntaxError("Unexpected closing parenthesis")

            else:
                expr = self.get_term()

                # Handle operations
                while self.match('OPERATOR') and not self.is_at_line_end():
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

                if expr:  # to prevent duplication due to keywords
                    args.append(expr)
                    expr = None

        if expect_closing_paren and self.peek().value != ')':
            raise SyntaxError("Expected closing parenthesis")
            
        return args, keywords

    def get_term(self) -> ast.AST:
        if self.match("STRING","CHAR"):
            return ast.Constant(value=self.advance().value.strip('"'))
        elif self.match("INTEGER"):
            value = self.advance().value
            return ast.Constant(value=int(value))
        elif self.match("REAL"):
            value = self.advance().value
            return ast.Constant(value=float(value))
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

    def print_handling(self) -> ast.AST:
        args, keywords = self.get_exp()
        if not args:
            raise Error(f"Expected expression after 'print' at line {self.peek().line}")
        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id='print', ctx=ast.Load()),
                args=args,
                keywords=keywords
            )
        )
    
    def if_handling(self) -> ast.AST:
        
        #TODO ,built diffrent get_exp() for condition and loop based keywords
        pass

def parse(tokens: List[Token]) -> ast.Module:
    """
    Parse tokens using parallel processing for large inputs,
    fall back to single-threaded parsing for small inputs.
    """
    if len(tokens) > 1000:  # Arbitrary threshold, adjust as needed
        return parse(tokens)
    else:
        parser = Parser(tokens)
        statements = []
        while not parser.is_at_file_end():
            statements.append(parser.parse_statement())
            if parser.is_at_line_end():
                parser.advance()
        return ast.Module(body=statements, type_ignores=[])
