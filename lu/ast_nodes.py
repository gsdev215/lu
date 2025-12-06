from dataclasses import dataclass
from typing import List, Optional, Any

# --- Statements / Program ---
@dataclass
class Program:
    statements: List['Stmt']

class Stmt: ...

@dataclass
class Block:
    statements: List['Stmt']

# Declarations / assignments
@dataclass
class DeclareStmt(Stmt):
    name: str
    array_size: Optional['Expr'] = None

@dataclass
class ConstantStmt(Stmt):
    name: str
    value: 'Expr'

@dataclass
class AssignStmt(Stmt):
    target: 'LValue'       # Variable or ArrayAccess or Attribute
    value: 'Expr'

# IO
@dataclass
class InputStmt(Stmt):
    name: str

@dataclass
class OutputStmt(Stmt):
    expr: 'Expr'

# Control flow
@dataclass
class IfStmt(Stmt):
    condition: 'Expr'
    then_block: Block
    else_block: Optional[Block]

@dataclass
class WhileStmt(Stmt):
    condition: 'Expr'
    body: Block

@dataclass
class ForStmt(Stmt):
    var: str
    start: 'Expr'
    end: 'Expr'
    step: Optional['Expr']
    body: Block

@dataclass
class RepeatUntilStmt(Stmt):
    body: Block
    condition: 'Expr'

# Functions / calls
@dataclass
class FunctionDef(Stmt):
    name: str
    params: List[str]
    body: Block

@dataclass
class ReturnStmt(Stmt):
    expr: Optional['Expr']

@dataclass
class CallStmt(Stmt):
    name: str
    args: List['Expr']

# Switch / Case
@dataclass
class CaseItem:
    value: 'Expr'
    body: Block

@dataclass
class SwitchStmt(Stmt):
    expr: 'Expr'
    cases: List[CaseItem]

# --- Expressions ---
class Expr: ...

@dataclass
class CallExpr(Expr):
    name: str
    args: List['Expr'] 

@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: str
    right: Expr

@dataclass
class UnaryExpr(Expr):
    op: str
    operand: Expr

@dataclass
class Literal(Expr):
    value: Any      # int, float, str, bool

@dataclass
class Variable(Expr):
    name: str

@dataclass
class ArrayAccess(Expr):
    array: Expr        # usually Variable
    index: Expr

@dataclass
class AttributeAccess(Expr):
    base: Expr
    attr: str

# LValue (for assignment targets)
class LValue: ...

# convenience typing aliases
ExprType = Expr
StmtType = Stmt
