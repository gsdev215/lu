
import ast
from typing import List, Any, Optional

from ast_nodes import Program, Block, DeclareStmt, ConstantStmt, AssignStmt, InputStmt, OutputStmt
from ast_nodes import IfStmt, WhileStmt, ForStmt, RepeatUntilStmt, FunctionDef, ReturnStmt, CallStmt
from ast_nodes import SwitchStmt, CaseItem, BinaryExpr, UnaryExpr, Literal, Variable, ArrayAccess, AttributeAccess
#
# For this snippet assume these classes are available in the namespace.

# ---------- Operator mapping helpers ----------
_binop_map = {
    '+': ast.Add(),
    '-': ast.Sub(),
    '*': ast.Mult(),
    '/': ast.Div(),
    '%': ast.Mod(),
    '^': ast.Pow(),   # we'll map '^' to Pow
}

_cmp_map = {
    '=': ast.Eq(), '==': ast.Eq(),
    '!=': ast.NotEq(), '<>': ast.NotEq(),
    '<': ast.Lt(), '<=': ast.LtE(),
    '>': ast.Gt(), '>=': ast.GtE(),
}

_boolop_map = {
    'AND': ast.And(),
    'OR': ast.Or(),
}

_unaryop_map = {
    '-': ast.USub(),
    '+': ast.UAdd(),
    'NOT': ast.Not(),
}


# ---------- Translator class ----------
class ASTCompiler:
    def __init__(self):
        # helper for generating unique temp names if needed
        self._tmp_count = 0

    def _fresh(self, prefix: str = "_tmp"):
        self._tmp_count += 1
        return f"{prefix}{self._tmp_count}"

    # Entry point
    def to_module(self, program) -> ast.Module:
        """Convert Program -> ast.Module"""
        body = []
        for stmt in program.statements:
            body_stmt = self._stmt_to_ast(stmt)
            # some stmt conversions return lists (multiple stmts), normalize
            if isinstance(body_stmt, list):
                body.extend(body_stmt)
            else:
                body.append(body_stmt)
        module = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(module)
        return module

    # ---------- Statements ----------
    def _stmt_to_ast(self, stmt):
        t = type(stmt).__name__

        dispatch = {
            'DeclareStmt': self._declare_to_ast,
            'ConstantStmt': self._constant_to_ast,
            'AssignStmt': self._assign_to_ast,
            'InputStmt': self._input_to_ast,
            'OutputStmt': self._output_to_ast,
            'IfStmt': self._if_to_ast,
            'WhileStmt': self._while_to_ast,
            'ForStmt': self._for_to_ast,
            'RepeatUntilStmt': self._repeat_to_ast,
            'FunctionDef': self._function_to_ast,
            'ReturnStmt': self._return_to_ast,
            'CallStmt': self._callstmt_to_ast,
            'SwitchStmt': self._switch_to_ast,
            'Block': self._block_to_list,  # in case someone passes Block directly
        }

        if t in dispatch:
            return dispatch[t](stmt)
        # Fallback: if it's an Expr as statement, wrap in Expr stmt
        if isinstance(stmt, (BinaryExpr, UnaryExpr, Literal, Variable, ArrayAccess, AttributeAccess)):
            return ast.Expr(value=self._expr_to_ast(stmt))
        raise NotImplementedError(f"No generator for statement type: {t}")

    def _block_to_list(self, block: 'Block'):
        out = []
        for s in block.statements:
            a = self._stmt_to_ast(s)
            if isinstance(a, list):
                out.extend(a)
            else:
                out.append(a)
        return out

    def _declare_to_ast(self, stmt: 'DeclareStmt'):
        # DECLARE x -> x = None
        # DECLARE x[size] -> x = [None] * size
        target = ast.Name(id=stmt.name, ctx=ast.Store())
        if stmt.array_size:
            size_expr = self._expr_to_ast(stmt.array_size)
            value = ast.BinOp(left=ast.List(elts=[ast.Constant(value=None)], ctx=ast.Load()),
                              op=ast.Mult(),
                              right=size_expr)
        else:
            value = ast.Constant(value=None)
        return ast.Assign(targets=[target], value=value)

    def _constant_to_ast(self, stmt: 'ConstantStmt'):
        target = ast.Name(id=stmt.name, ctx=ast.Store())
        value = self._expr_to_ast(stmt.value)
        return ast.Assign(targets=[target], value=value)

    def _assign_to_ast(self, stmt: 'AssignStmt'):
        target_node = self._lvalue_to_ast(stmt.target, store=True)
        value_node = self._expr_to_ast(stmt.value)
        return ast.Assign(targets=[target_node], value=value_node)

    def _input_to_ast(self, stmt: 'InputStmt'):
        # name = input()
        call = ast.Call(func=ast.Name(id='input', ctx=ast.Load()), args=[], keywords=[])
        target = ast.Name(id=stmt.name, ctx=ast.Store())
        return ast.Assign(targets=[target], value=call)

    def _output_to_ast(self, stmt: 'OutputStmt'):
        # print(expr)
        call = ast.Call(func=ast.Name(id='print', ctx=ast.Load()),
                        args=[self._expr_to_ast(stmt.expr)],
                        keywords=[])
        return ast.Expr(value=call)

    def _if_to_ast(self, stmt: 'IfStmt'):
        test = self._expr_to_ast(stmt.condition)
        then_body = self._block_to_list(stmt.then_block)
        else_body = self._block_to_list(stmt.else_block) if stmt.else_block else []
        return ast.If(test=test, body=then_body, orelse=else_body)

    def _while_to_ast(self, stmt: 'WhileStmt'):
        test = self._expr_to_ast(stmt.condition)
        body = self._block_to_list(stmt.body)
        return ast.While(test=test, body=body, orelse=[])

    def _for_to_ast(self, stmt: 'ForStmt'):
        """
        Translate IGCSE FOR var = start TO end [STEP step] ... NEXT
        into Python using a while loop so inclusive semantics are preserved.
        """
        var_name = stmt.var
        start = self._expr_to_ast(stmt.start)
        end = self._expr_to_ast(stmt.end)
        step_expr = self._expr_to_ast(stmt.step) if stmt.step is not None else ast.Constant(value=1)

        # var = start
        init = ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=start)

        # condition: if step > 0: var <= end else var >= end
        # create a runtime test: (step > 0 and var <= end) or (step <= 0 and var >= end)
        step_name = self._fresh("_for_step")
        # create step temp: _for_step = <step_expr>
        step_assign = ast.Assign(targets=[ast.Name(id=step_name, ctx=ast.Store())], value=step_expr)

        # test expression
        step_pos = ast.Compare(left=ast.Name(id=step_name, ctx=ast.Load()),
                               ops=[ast.Gt()],
                               comparators=[ast.Constant(value=0)])
        cond_pos = ast.Compare(left=ast.Name(id=var_name, ctx=ast.Load()),
                               ops=[ast.LtE()],
                               comparators=[end])
        cond_neg = ast.Compare(left=ast.Name(id=var_name, ctx=ast.Load()),
                               ops=[ast.GtE()],
                               comparators=[end])
        test = ast.BoolOp(op=ast.Or(),
                          values=[ast.BoolOp(op=ast.And(), values=[step_pos, cond_pos]),
                                  ast.BoolOp(op=ast.And(), values=[ast.UnaryOp(op=ast.Not(), operand=step_pos), cond_neg])])

        # body
        body = self._block_to_list(stmt.body)
        # increment: var = var + _for_step
        incr = ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())],
                          value=ast.BinOp(left=ast.Name(id=var_name, ctx=ast.Load()),
                                          op=ast.Add(),
                                          right=ast.Name(id=step_name, ctx=ast.Load())))
        body.append(incr)

        # while loop
        while_stmt = ast.While(test=test, body=body, orelse=[])
        # produce sequence: init, step_assign, while
        return [init, step_assign, while_stmt]

    def _repeat_to_ast(self, stmt: 'RepeatUntilStmt'):
        # Translate: REPEAT body UNTIL cond
        # to:
        # while True:
        #     <body>
        #     if cond:
        #         break
        body = self._block_to_list(stmt.body)
        cond = self._expr_to_ast(stmt.condition)
        if_stmt = ast.If(test=cond, body=[ast.Break()], orelse=[])
        body.append(if_stmt)
        while_node = ast.While(test=ast.Constant(value=True), body=body, orelse=[])
        return while_node

    def _function_to_ast(self, stmt: 'FunctionDef'):
        args = [ast.arg(arg=name, annotation=None) for name in stmt.params]
        args_node = ast.arguments(posonlyargs=[], args=args, vararg=None, kwonlyargs=[],
                                  kw_defaults=[], kwarg=None, defaults=[])
        body = self._block_to_list(stmt.body)
        # Ensure function has at least a pass
        if not body:
            body = [ast.Pass()]
        func = ast.FunctionDef(name=stmt.name, args=args_node, body=body, decorator_list=[]) # type: ignore
        return func

    def _return_to_ast(self, stmt: 'ReturnStmt'):
        if stmt.expr is None:
            return ast.Return(value=None)
        return ast.Return(value=self._expr_to_ast(stmt.expr))

    def _callstmt_to_ast(self, stmt: 'CallStmt'):
        call = ast.Call(func=ast.Name(id=stmt.name, ctx=ast.Load()),
                        args=[self._expr_to_ast(a) for a in stmt.args],
                        keywords=[])
        return ast.Expr(value=call)

    def _switch_to_ast(self, stmt: 'SwitchStmt'):
        # Translate to if/elif chain:
        # if expr == case1: <body>
        # elif expr == case2: <body>
        # ...
        scrut = self._expr_to_ast(stmt.expr)
        if not stmt.cases:
            return ast.Pass()
        nodes = []
        first = True
        last_node = None
        for case in stmt.cases:
            test = ast.Compare(left=scrut, ops=[ast.Eq()], comparators=[self._expr_to_ast(case.value)])
            body = self._block_to_list(case.body)
            if first:
                if_node = ast.If(test=test, body=body, orelse=[])
                nodes.append(if_node)
                last_node = if_node
                first = False
            else:
                # attach as elif by appending to previous orelse
                new_if = ast.If(test=test, body=body, orelse=[])
                last_node.orelse = [new_if] # type: ignore
                last_node = new_if
        return nodes[0] if nodes else ast.Pass()

    # ---------- LValue (target) ----------
    def _lvalue_to_ast(self, target, store: bool = True):
        """Return an AST node usable on LHS. If store True, ctx=Store else Load."""
        ctx = ast.Store() if store else ast.Load()
        if isinstance(target, Variable):
            return ast.Name(id=target.name, ctx=ctx)
        if isinstance(target, ArrayAccess):
            value = self._expr_to_ast(target.array)
            index = self._expr_to_ast(target.index)
            return ast.Subscript(value=value, slice=ast.Index(value=index), ctx=ctx)
        if isinstance(target, AttributeAccess):
            base = self._expr_to_ast(target.base)
            return ast.Attribute(value=base, attr=target.attr, ctx=ctx)
        # fallback: try expression
        expr_node = self._expr_to_ast(target)
        if isinstance(expr_node, ast.Subscript):
            expr_node.ctx = ctx
            return expr_node
        raise NotImplementedError(f"Unsupported LValue node type: {type(target).__name__}")

    # ---------- Expressions ----------
    def _expr_to_ast(self, expr):
        if isinstance(expr, Literal):
            return ast.Constant(value=expr.value)
        if isinstance(expr, Variable):
            return ast.Name(id=expr.name, ctx=ast.Load())
        if isinstance(expr, ArrayAccess):
            val = self._expr_to_ast(expr.array)
            idx = self._expr_to_ast(expr.index)
            return ast.Subscript(value=val, slice=ast.Index(value=idx), ctx=ast.Load())
        if isinstance(expr, AttributeAccess):
            base = self._expr_to_ast(expr.base)
            return ast.Attribute(value=base, attr=expr.attr, ctx=ast.Load())
        if isinstance(expr, UnaryExpr):
            # unary op could be NOT, +, -
            op = expr.op.upper() if isinstance(expr.op, str) else expr.op
            if op == 'NOT':
                return ast.UnaryOp(op=ast.Not(), operand=self._expr_to_ast(expr.operand))
            if op in _unaryop_map:
                return ast.UnaryOp(op=_unaryop_map[op], operand=self._expr_to_ast(expr.operand))
            # fallback
            return ast.UnaryOp(op=ast.UAdd(), operand=self._expr_to_ast(expr.operand))
        if isinstance(expr, BinaryExpr):
            op = expr.op
            # boolean ops
            if isinstance(op, str) and op.upper() in _boolop_map:
                return ast.BoolOp(op=_boolop_map[op.upper()], values=[self._expr_to_ast(expr.left),
                                                                      self._expr_to_ast(expr.right)])
            # comparison ops
            if op in _cmp_map:
                return ast.Compare(left=self._expr_to_ast(expr.left),
                                   ops=[_cmp_map[op]],
                                   comparators=[self._expr_to_ast(expr.right)])
            # arithmetic / binary ops
            if op in _binop_map:
                return ast.BinOp(left=self._expr_to_ast(expr.left),
                                 op=_binop_map[op],
                                 right=self._expr_to_ast(expr.right))
            # fallback to compare if op is '=' or '==' handled above
            # else try to generate a call (e.g., unsupported op)
            # We'll treat unknown ops as function calls: op(left, right)
            return ast.Call(func=ast.Name(id=str(op), ctx=ast.Load()),
                            args=[self._expr_to_ast(expr.left), self._expr_to_ast(expr.right)],
                            keywords=[])
        if isinstance(expr, CallStmt):  # sometimes parser may use Call as expression form
            return ast.Call(func=ast.Name(id=expr.name, ctx=ast.Load()),
                            args=[self._expr_to_ast(a) for a in expr.args],
                            keywords=[])
        # Unknown expression type
        raise NotImplementedError(f"Unsupported Expr node: {type(expr).__name__}")

# ---------- Top-level utility functions ----------
def to_python_ast(program) -> ast.Module:
    compiler = ASTCompiler()
    return compiler.to_module(program)

def compile_and_exec(program, global_ns: Optional[dict] = None):
    """
    Compile custom Program into python AST, compile it, and exec in global_ns.
    Returns (code_obj, module_ast).
    """
    module_ast = to_python_ast(program)
    code_obj = compile(module_ast, filename='<generated>', mode='exec')
    if global_ns is None:
        global_ns = {}
    exec(code_obj, global_ns)
    return code_obj, module_ast

# ---------- Example usage ----------
if __name__ == "__main__":
    # simple manual test (requires your AST classes)
    # from ast_nodes import Program, AssignStmt, Variable, Literal
    #
    # p = Program(statements=[
    #     AssignStmt(target=Variable("x"), value=Literal(10)),
    #     AssignStmt(target=Variable("y"), value=Literal(20)),
    #     CallStmt(name="print", args=[BinaryExpr(left=Variable("x"), op="+", right=Variable("y"))])
    # ])
    #
    # code_obj, module_ast = compile_and_exec(p, globals())
    # print(ast.dump(module_ast, include_attributes=False, indent=2))
    #
    pass
