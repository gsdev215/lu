import ast
from typing import List, Dict, Any

# WARNING! used AI for genrating this file , might content many logical errors also i have no idea why i genrated this do not ask ! , would rewrite it later


class Compiler:
    def __init__(self):
        self.indent = 0
        self.output = []
        self.variables: Dict[str, str] = {}  # Track variable types

    def compile(self, node: ast.AST) -> str:
        self.visit(node)
        return "\n".join(self.output)

    def visit(self, node: ast.AST):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ast.AST):
        raise Exception(f"No visit method for {type(node).__name__}")

    def add_line(self, line: str):
        self.output.append("    " * self.indent + line)

    def visit_Module(self, node: ast.Module):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Assign(self, node: ast.Assign):
        value = self.visit(node.value)
        for target in node.targets:
            target_name = self.visit(target)
            self.add_line(f"{target_name} = {value}")

    def visit_Expr(self, node: ast.Expr):
        self.visit(node.value)

    def visit_Call(self, node: ast.Call):
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        keywords = [f"{kw.arg}={self.visit(kw.value)}" for kw in node.keywords]
        all_args = ", ".join(args + keywords)
        
        if func == "print":
            self.add_line(f"print({all_args})")
        else:
            return f"{func}({all_args})"

    def visit_If(self, node: ast.If):
        condition = self.visit(node.test)
        self.add_line(f"if {condition}:")
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1
        if node.orelse:
            self.add_line("else:")
            self.indent += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent -= 1

    def visit_While(self, node: ast.While):
        condition = self.visit(node.test)
        self.add_line(f"while {condition}:")
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1

    def visit_For(self, node: ast.For):
        target = self.visit(node.target)
        iter_expr = self.visit(node.iter)
        self.add_line(f"for {target} in {iter_expr}:")
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef):
        params = ", ".join(self.visit(arg) for arg in node.args.args)
        self.add_line(f"def {node.name}({params}):")
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1

    def visit_Return(self, node: ast.Return):
        if node.value:
            value = self.visit(node.value)
            self.add_line(f"return {value}")
        else:
            self.add_line("return")

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.visit(node.op)
        return f"({left} {op} {right})"

    def visit_UnaryOp(self, node: ast.UnaryOp):
        operand = self.visit(node.operand)
        op = self.visit(node.op)
        return f"({op}{operand})"

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    def visit_Name(self, node: ast.Name):
        return node.id

    def visit_List(self, node: ast.List):
        elements = ", ".join(self.visit(elem) for elem in node.elts)
        return f"[{elements}]"

    def visit_Dict(self, node: ast.Dict):
        elements = ", ".join(f"{self.visit(k)}: {self.visit(v)}" for k, v in zip(node.keys, node.values))
        return f"{{{elements}}}"

    def visit_Subscript(self, node: ast.Subscript):
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        return f"{value}[{slice}]"

    def visit_Attribute(self, node: ast.Attribute):
        value = self.visit(node.value)
        return f"{value}.{node.attr}"

    # Operator visit methods
    def visit_Add(self, node): return "+"
    def visit_Sub(self, node): return "-"
    def visit_Mult(self, node): return "*"
    def visit_Div(self, node): return "/"
    def visit_Mod(self, node): return "%"
    def visit_Pow(self, node): return "**"
    def visit_LShift(self, node): return "<<"
    def visit_RShift(self, node): return ">>"
    def visit_BitOr(self, node): return "|"
    def visit_BitXor(self, node): return "^"
    def visit_BitAnd(self, node): return "&"
    def visit_FloorDiv(self, node): return "//"

    # Comparison operators
    def visit_Eq(self, node): return "=="
    def visit_NotEq(self, node): return "!="
    def visit_Lt(self, node): return "<"
    def visit_LtE(self, node): return "<="
    def visit_Gt(self, node): return ">"
    def visit_GtE(self, node): return ">="
    def visit_Is(self, node): return "is"
    def visit_IsNot(self, node): return "is not"
    def visit_In(self, node): return "in"
    def visit_NotIn(self, node): return "not in"

    def visit_BoolOp(self, node: ast.BoolOp):
        op = "and" if isinstance(node.op, ast.And) else "or"
        return f" {op} ".join(self.visit(value) for value in node.values)

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        comparisons = []
        for op, right in zip(node.ops, node.comparators):
            comparisons.append(f"{self.visit(op)} {self.visit(right)}")
        return f"{left} {' '.join(comparisons)}"

    def visit_arg(self, node: ast.arg):
        return node.arg

def compile_to_python(ast_node: ast.AST) -> str:
    compiler = Compiler()
    return compiler.compile(ast_node)