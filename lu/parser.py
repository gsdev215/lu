from typing import List, Optional, Set
from lexer import Token

# Assuming these AST nodes exist in ast_nodes.py. 
# Added 'CallExpr' which is necessary for function calls inside expressions.
from ast_nodes import (
    Program, Block, DeclareStmt, ConstantStmt, AssignStmt,
    InputStmt, OutputStmt, IfStmt, WhileStmt, ForStmt, RepeatUntilStmt,
    FunctionDef, ReturnStmt, CallStmt, SwitchStmt, CaseItem,
    BinaryExpr, UnaryExpr, Literal, Variable, ArrayAccess, AttributeAccess,
    CallExpr 
)

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List['Token']):
        self.tokens = tokens
        self.i = 0

    # ----- Token Helpers -----
    
    def peek(self) -> 'Token':
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return self.tokens[-1]

    def peek_next(self) -> Optional['Token']:
        if self.i + 1 < len(self.tokens):
            return self.tokens[self.i + 1]
        return None

    def advance(self) -> 'Token':
        tok = self.peek()
        if self.i < len(self.tokens):
            self.i += 1
        return tok

    def match_type(self, t: str) -> Optional['Token']:
        if self.peek().type == t:
            return self.advance()
        return None

    def match_keyword(self, *kw) -> Optional['Token']:
        tok = self.peek()
        if tok.type == 'KEYWORD' and tok.value.upper() in kw:
            return self.advance()
        return None

    def match_value(self, value: str) -> Optional['Token']:
        tok = self.peek()
        if tok.value == value:
            return self.advance()
        return None

    def expect_type(self, t: str) -> 'Token':
        tok = self.peek()
        if tok.type != t:
            line = getattr(tok, 'line', '?')
            raise ParseError(f"Expected token type {t} but got {tok.type}({tok.value}) at line {line}")
        return self.advance()

    def expect_keyword(self, kw: str) -> 'Token':
        tok = self.peek()
        if tok.type != 'KEYWORD' or tok.value.upper() != kw:
            line = getattr(tok, 'line', '?')
            raise ParseError(f"Expected keyword '{kw}' but got {tok.type}({tok.value}) at line {line}")
        return self.advance()

    def expect_value(self, value: str) -> 'Token':
        tok = self.peek()
        if tok.value != value:
            line = getattr(tok, 'line', '?')
            raise ParseError(f"Expected symbol '{value}' but got {tok.value} at line {line}")
        return self.advance()

    # ----- Entrypoint -----
    
    def parse(self) -> Program:
        stmts = self.parse_statement_list()
        if self.peek().type != 'EOF':
            raise ParseError(f"Expected EOF, found {self.peek().value}")
        return Program(statements=stmts)

    # ----- Statements -----
    
    def parse_statement_list(self, stop_on: Optional[Set[str]] = None) -> List:
        """Parse zero or more statements until lookahead is in stop_on or EOF."""
        stmts = []
        if stop_on is None:
            stop_on = {'ELSE', 'ENDIF', 'ENDWHILE', 'NEXT', 'UNTIL', 'ENDFUNCTION', 'ENDCASE', 'ENDSWITCH', 'EOF'}
        
        while True:
            tok = self.peek()
            if tok.type == 'EOF':
                break
            if tok.type == 'KEYWORD' and tok.value.upper() in stop_on:
                break
            
            # Skip stray newlines/delimiters if necessary, though lexer usually handles this.
            # Here we rely on parse_statement handling leading newlines.
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def parse_statement(self):
        # Consume empty lines first
        while self.peek().type == 'NEWLINE':
            self.advance()
            
        tok = self.peek()
        
        # 1. Keywords
        if tok.type == 'KEYWORD':
            v = tok.value.upper()
            if v == 'DECLARE':      return self.parse_declare()
            if v == 'CONSTANT':     return self.parse_constant()
            if v == 'INPUT':        return self.parse_input()
            if v in ('OUTPUT', 'PRINT'): return self.parse_output()
            if v == 'IF':           return self.parse_if()
            if v == 'WHILE':        return self.parse_while()
            if v == 'FOR':          return self.parse_for()
            if v == 'REPEAT':       return self.parse_repeat()
            if v == 'FUNCTION':     return self.parse_function_def()
            if v == 'RETURN':       return self.parse_return()
            if v == 'CALL':         return self.parse_call_stmt()
            if v == 'SWITCH':       return self.parse_switch()
            # If we hit a stop_on keyword (like ELSE), we return None so the list loop breaks
            return None

        # 2. Identifiers (Assignment vs Function Call)
        if tok.type == 'IDENTIFIER':
            nxt = self.peek_next()
            # If IDENTIFIER is followed by '(', it's a standalone function call
            # e.g. MyFunction(10)
            if nxt and nxt.value == '(':
                return self.parse_call_stmt(allow_simple_call=True)
            else:
                return self.parse_assignment()

        if tok.type == 'EOF':
            return None

        raise ParseError(f"Unexpected token in statement: {tok.type}({tok.value})")

    # --- Declarations ---
    
    def parse_declare(self) -> DeclareStmt:
        self.expect_keyword('DECLARE')
        name_tok = self.expect_type('IDENTIFIER')
        array_size = None
        if self.match_value('['):
            array_size = self.parse_expr()
            self.expect_value(']')
        
        # Optional: Parse type (e.g., DECLARE x : INTEGER)
        # If your grammar supports ": TYPE", add it here.
        
        return DeclareStmt(name=name_tok.value, array_size=array_size)

    def parse_constant(self) -> ConstantStmt:
        self.expect_keyword('CONSTANT')
        name = self.expect_type('IDENTIFIER').value
        
        # Support both '=' and '<-' if necessary, strict '=' here
        op = self.peek()
        if op.type == 'OPERATOR' and op.value == '=':
            self.advance()
        else:
            raise ParseError("Expected '=' in constant declaration")
            
        val = self.parse_expr()
        return ConstantStmt(name=name, value=val)

    # --- Assignment ---
    
    def parse_assignment(self) -> AssignStmt:
        # 1. Parse LHS (L-Value)
        target = self.parse_lvalue()
        
        # 2. Expect assignment operator
        op = self.peek()
        if op.type == 'OPERATOR' and op.value in ('=', '<-'): # Allow <- for pseudocode
            self.advance()
        else:
            raise ParseError(f"Expected '=' or '<-' for assignment, got {op.value}")
            
        # 3. Parse RHS
        value = self.parse_expr()
        return AssignStmt(target=target, value=value)

    def parse_lvalue(self):
        """Parses a variable, array access, or attribute access chain."""
        base_tok = self.expect_type('IDENTIFIER')
        node = Variable(name=base_tok.value)
        # Delegate to shared helper to process [idx] or .attr
        return self._parse_access_chain(node)

    def _parse_access_chain(self, node):
        """Helper to recursively parse [index] and .attribute access."""
        while True:
            # Array Access
            if self.match_value('['):
                idx = self.parse_expr()
                self.expect_value(']')
                node = ArrayAccess(array=node, index=idx)
                continue
            
            # Attribute Access (Explicit dot delimiter)
            if self.peek().type == 'DELIMITER' and self.peek().value == '.':
                self.advance()
                attr_tok = self.expect_type('IDENTIFIER')
                node = AttributeAccess(base=node, attr=attr_tok.value)
                continue
                
            # Attribute Access (Lexer optimized token)
            if self.peek().type == 'ATTRIBUTE':
                attr_value = self.advance().value
                attr_name = attr_value.lstrip('.')
                node = AttributeAccess(base=node, attr=attr_name)
                continue
                
            break
        return node

    # --- I/O ---
    
    def parse_input(self) -> InputStmt:
        self.expect_keyword('INPUT')
        # Logic allows `INPUT x`
        # To allow `INPUT "Prompt", x`, check for string literal first
        if self.peek().type == 'STRING':
            self.advance() # consume prompt
            if self.match_value(','):
                pass
        name = self.expect_type('IDENTIFIER').value
        return InputStmt(name=name)

    def parse_output(self) -> OutputStmt:
        self.advance()  # Consumes OUTPUT or PRINT
        expr = self.parse_expr()
        # Optional: Support comma separated list: PRINT a, b, c
        return OutputStmt(expr=expr)

    # --- Control Flow ---
    
    def parse_if(self) -> IfStmt:
        self.expect_keyword('IF')
        cond = self.parse_expr()
        self.expect_keyword('THEN')
        
        then_stmts = self.parse_statement_list(stop_on={'ELSE', 'ENDIF'})
        then_block = Block(statements=then_stmts)
        else_block = None
        
        if self.match_keyword('ELSE'):
            else_stmts = self.parse_statement_list(stop_on={'ENDIF'})
            else_block = Block(statements=else_stmts)
            
        self.expect_keyword('ENDIF')
        return IfStmt(condition=cond, then_block=then_block, else_block=else_block)

    def parse_while(self) -> WhileStmt:
        self.expect_keyword('WHILE')
        cond = self.parse_expr()
        self.match_keyword('DO') # Optional DO
        
        body_stmts = self.parse_statement_list(stop_on={'ENDWHILE'})
        self.expect_keyword('ENDWHILE')
        return WhileStmt(condition=cond, body=Block(statements=body_stmts))

    def parse_for(self) -> ForStmt:
        self.expect_keyword('FOR')
        var = self.expect_type('IDENTIFIER').value
        
        # Expect '=' or '<-'
        if self.peek().type == 'OPERATOR' and self.peek().value in ('=', '<-'):
            self.advance()
        else:
            raise ParseError("Expected '=' in FOR initialiser")
            
        start = self.parse_expr()
        self.expect_keyword('TO')
        end = self.parse_expr()
        
        step = None
        if self.match_keyword('STEP'):
            step = self.parse_expr()
            
        body_stmts = self.parse_statement_list(stop_on={'NEXT'})
        self.expect_keyword('NEXT')
        
        # Optional: Allow NEXT <var> (e.g. NEXT i)
        if self.peek().type == 'IDENTIFIER':
            if self.peek().value == var:
                self.advance()
            else:
                # Depending on strictness, we might warn or ignore. 
                # For now, we assume if an identifier exists, it must match.
                # If it doesn't match, we assume it's the start of the next statement 
                # (unless it's strictly required by grammar).
                pass 
                
        return ForStmt(var=var, start=start, end=end, step=step, body=Block(statements=body_stmts))

    def parse_repeat(self) -> RepeatUntilStmt:
        self.expect_keyword('REPEAT')
        body_stmts = self.parse_statement_list(stop_on={'UNTIL'})
        self.expect_keyword('UNTIL')
        cond = self.parse_expr()
        return RepeatUntilStmt(body=Block(statements=body_stmts), condition=cond)

    # --- Functions ---
    
    def parse_function_def(self) -> FunctionDef:
        self.expect_keyword('FUNCTION')
        name = self.expect_type('IDENTIFIER').value
        self.expect_value('(')
        params = []
        if self.peek().type == 'IDENTIFIER':
            params.append(self.expect_type('IDENTIFIER').value)
            while self.match_value(','):
                params.append(self.expect_type('IDENTIFIER').value)
        self.expect_value(')')
        
        body_stmts = self.parse_statement_list(stop_on={'ENDFUNCTION'})
        self.expect_keyword('ENDFUNCTION')
        return FunctionDef(name=name, params=params, body=Block(statements=body_stmts))

    def parse_return(self) -> ReturnStmt:
        self.expect_keyword('RETURN')
        
        # Logic Fix: Check for start of expression including unary ops
        tok = self.peek()
        is_expr_start = (
            tok.type in ('IDENTIFIER', 'INTEGER', 'REAL', 'STRING', 'CHAR', 'BOOLEAN') or
            tok.value in ('(', '+', '-') or
            (tok.type == 'KEYWORD' and tok.value.upper() == 'NOT')
        )
        
        if is_expr_start:
            expr = self.parse_expr()
            return ReturnStmt(expr=expr)
        return ReturnStmt(expr=None)

    def parse_call_stmt(self, allow_simple_call=False) -> CallStmt:
        if self.peek().type == 'KEYWORD' and self.peek().value.upper() == 'CALL':
            self.advance()
            name = self.expect_type('IDENTIFIER').value
        elif allow_simple_call:
            name = self.expect_type('IDENTIFIER').value
        else:
            raise ParseError("Expected CALL or Function Name")

        self.expect_value('(')
        args = []
        if self.peek().value != ')':
            args.append(self.parse_expr())
            while self.match_value(','):
                args.append(self.parse_expr())
        self.expect_value(')')
        return CallStmt(name=name, args=args)

    def parse_switch(self) -> SwitchStmt:
        self.expect_keyword('SWITCH')
        expr = self.parse_expr()
        cases = []
        
        # Some dialects allow newline before first CASE, some don't.
        while self.peek().type == 'NEWLINE': 
            self.advance()
            
        while self.match_keyword('CASE'):
            val = self.parse_expr()
            if self.peek().value == ':':
                self.advance()
                
            body_stmts = self.parse_statement_list(stop_on={'ENDCASE', 'CASE', 'DEFAULT', 'ENDSWITCH'})
            cases.append(CaseItem(value=val, body=Block(statements=body_stmts)))
            
            # Handle possible DEFAULT (not in original code, but standard)
            if self.peek().type == 'KEYWORD' and self.peek().value.upper() == 'DEFAULT':
                # Parse default block if needed, or error out if not supported
                pass 
                
        self.expect_keyword('ENDSWITCH')
        return SwitchStmt(expr=expr, cases=cases)

    # --------------------- Expressions ---------------------
    
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.peek().type == 'KEYWORD' and self.peek().value.upper() == 'OR':
            op = self.advance().value.upper()
            right = self.parse_and()
            node = BinaryExpr(left=node, op=op, right=right)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.peek().type == 'KEYWORD' and self.peek().value.upper() == 'AND':
            op = self.advance().value.upper()
            right = self.parse_not()
            node = BinaryExpr(left=node, op=op, right=right)
        return node

    def parse_not(self):
        if self.peek().type == 'KEYWORD' and self.peek().value.upper() == 'NOT':
            op = self.advance().value.upper()
            operand = self.parse_not()
            return UnaryExpr(op=op, operand=operand)
        return self.parse_compare()

    def parse_compare(self):
        node = self.parse_add()
        if self.peek().type == 'OPERATOR' and self.peek().value in ('=','==','!=','<>','<=','>=','<','>'):
            op = self.advance().value
            right = self.parse_add()
            node = BinaryExpr(left=node, op=op, right=right)
        return node

    def parse_add(self):
        node = self.parse_mul()
        while self.peek().type == 'OPERATOR' and self.peek().value in ('+','-'):
            op = self.advance().value
            right = self.parse_mul()
            node = BinaryExpr(left=node, op=op, right=right)
        return node

    def parse_mul(self):
        node = self.parse_pow()
        while self.peek().type == 'OPERATOR' and self.peek().value in ('*','/','%','MOD','DIV'): # Added MOD/DIV words
            op = self.advance().value
            right = self.parse_pow()
            node = BinaryExpr(left=node, op=op, right=right)
        return node

    def parse_pow(self):
        node = self.parse_factor()
        if self.peek().type == 'OPERATOR' and self.peek().value == '^':
            op = self.advance().value
            right = self.parse_pow()
            node = BinaryExpr(left=node, op=op, right=right)
        return node

    def parse_factor(self):
        tok = self.peek()
        
        # 1. Literals
        if tok.type in ('INTEGER','REAL','STRING','CHAR','BOOLEAN'):
            self.advance()
            val = tok.value
            if tok.type == 'INTEGER':
                val = int(tok.value)
            elif tok.type == 'REAL':
                val = float(tok.value)
            elif tok.type == 'BOOLEAN':
                val = tok.value.upper() == 'TRUE'
            elif tok.type == 'STRING':
                if val.startswith('"') and val.endswith('"'): val = val[1:-1]
            elif tok.type == 'CHAR':
                if val.startswith("'") and val.endswith("'"): val = val[1:-1]
            return Literal(value=val)

        # 2. Parentheses
        if tok.value == '(':
            self.advance()
            node = self.parse_expr()
            self.expect_value(')')
            return node

        # 3. Unary Operators (+, -)
        if tok.type == 'OPERATOR' and tok.value in ('-','+'):
            op = self.advance().value
            right = self.parse_factor()
            return UnaryExpr(op=op, operand=right)

        # 4. Identifiers (Variable OR Function Call)
        if tok.type == 'IDENTIFIER':
            # Check for Function Call: ident(...)
            if self.peek_next() and self.peek_next().value == '(':
                return self.parse_call_expr()
            
            # Check for Variable / Array / Attribute
            base = Variable(name=self.advance().value)
            return self._parse_access_chain(base)

        raise ParseError(f"Unexpected token in factor: {tok.type}({tok.value}) line {getattr(tok, 'line', '?')}")

    def parse_call_expr(self) -> CallExpr:
        """Parses a function call used inside an expression."""
        name = self.expect_type('IDENTIFIER').value
        self.expect_value('(')
        args = []
        if self.peek().value != ')':
            args.append(self.parse_expr())
            while self.match_value(','):
                args.append(self.parse_expr())
        self.expect_value(')')
        return CallExpr(name=name, args=args)