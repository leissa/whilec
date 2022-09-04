from loc import *

class AST:
    def __init__(self, loc): self.loc = loc

# Stmt

class Stmt(AST):
    def __init__(self, loc): super(Stmt, self).__init__(loc)

class AssignStmt(Stmt):
    def __init__(self, loc, id, expr):
        super(AssignStmt, self).__init__(loc)
        self.id   = id
        self.expr = expr

    def __str__(self): return f'{self.id} = {self.lhs} {self.op} {self.rhs}'

class WhileStmt(Stmt):
    def __init__(self, loc, cond, body):
        super(WhileStmt, self).__init__(loc)
        self.cond = cond
        self.body = body

# Expr

class Expr(AST):
    def __init__(self, loc): super(Expr, self).__init__(loc)

class IdExpr(Expr):
    def __init__(self, loc, id):
        super(IdExpr, self).__init__(loc)
        self.id = id

    def __str__(self): return f'{self.id}'

class LitExpr(Expr):
    def __init__(self, loc, lit):
        super(LitExpr, self).__init__(loc)
        self.lit = lit

    def __str__(self): return f'{self.lit}'

class BinExpr(Expr):
    def __init__(self, loc, lhs, op, rhs):
        super(BinExpr, self).__init__(loc)
        self.lhs = lhs
        self.op  = op
        self.rhs = rhs

    def __str__(self): return f'({self.lhs} {self.op} {self.rhs})'

# Bool

class LitBool(Expr):
    def __init__(self, loc, lit):
        super(LitExpr, self).__init__(loc)
        self.lit = lit

    def __str__(self): return f'{self.lit}'
