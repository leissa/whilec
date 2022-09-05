from tok import *
from err import *

class Tab:
    def __init__(self, tab = "\t"):
        self.ind = 0
        self.tab = tab

    def indent(self): self.ind += 1
    def dedent(self): self.ind -= 1
    def __str__(self):
        res = ""
        for i in range(self.ind):
            res += self.tab
        return res

tab = Tab()

class Sema:
    def __init__(self):
        self.scope = {}

    def find(self, tok):
        if tok.id in self.scope: return self.scope[tok.id]
        err(tok.loc, f"identifier '{tok}' not found")
        return None

    def bind(self, tok, decl):
        if tok.id in self.scope:
            err(tok.loc, f"identifier '{tok}' already declared here: {self.scope[tok.id].loc}")
            return False

        self.scope[tok.id] = decl
        return True

# AST

class AST:
    def __init__(self, loc):
        self.loc = loc

class Prog(AST):
    def __init__(self, loc, stmt, ret):
        super(Prog, self).__init__(loc)
        self.stmt = stmt
        self.ret  = ret

    def __str__(self):
        head = f"{self.stmt}"
        tail = f"return {self.ret};"
        return head + tail

    def check(self):
        sema = Sema()
        self.stmt.check(sema)
        self.ret.check(sema)

# Stmt

class Stmt(AST):
    def __init__(self, loc): super(Stmt, self).__init__(loc)

class DeclStmt(Stmt):
    def __init__(self, loc, type, id, expr):
        super(DeclStmt, self).__init__(loc)
        self.type = type
        self.id   = id
        self.expr = expr

    def __str__(self):
        return f"{self.type} {self.id} = {self.expr}"

    def check(self, sema):
        self.expr.check(sema)
        sema.bind(self.id, self)

class AssignStmt(Stmt):
    def __init__(self, loc, id, expr):
        super(AssignStmt, self).__init__(loc)
        self.id   = id
        self.expr = expr

    def __str__(self):
        return f"{self.id}: {self.type} = {self.expr}"

    def check(self, sema):
        self.expr.check(sema)
        sema.find(self.id)

class StmtList(Stmt):
    def __init__(self, loc, stmts):
        super(StmtList, self).__init__(loc)
        self.stmts = stmts

    def __str__(self):
        res = ""
        for stmt in self.stmts:
            res += f"{tab}{stmt};\n"
        return res

    def check(self, sema):
        for stmt in self.stmts: stmt.check(sema)

class WhileStmt(Stmt):
    def __init__(self, loc, cond, body):
        super(WhileStmt, self).__init__(loc)
        self.cond = cond
        self.body = body

    def __str__(self):
        head = f"while {self.cond} {{\n"
        tab.indent()
        body = f"{self.body}"
        tab.dedent()
        tail = f"{tab}}}"
        return head + body + tail

    def check(self, sema):
        self.cond.check(sema)
        self.body.check(sema)

# Expr

class Expr(AST):
    def __init__(self, loc):
        super(Expr, self).__init__(loc)
        self.type = None

class BinExpr(Expr):
    def __init__(self, loc, lhs, op, rhs):
        super(BinExpr, self).__init__(loc)
        self.lhs = lhs
        self.op  = op
        self.rhs = rhs

    def __str__(self): return f"({self.lhs} {self.op} {self.rhs})"

    def check(self, sema):
        t = self.lhs.check(sema)
        u = self.rhs.check(sema)

        if self.op.is_arith():
            x = Tag.K_int
            r = Tag.K_int
        elif self.op.is_rel():
            x = Tag.K_int
            r = Tag.K_bool
        elif self.op.is_logic():
            x = Tag.K_bool
            r = Tag.K_bool
        else:
            assert False

        if t != None and t is not x: err(self.lhs.loc,  f"left-hand side of operator '{self.op}' must be of type '{x}' but is of type '{t}'")
        if u != None and u is not x: err(self.rhs.loc, f"right-hand side of operator '{self.op}' must be of type '{x}' but is of type '{u}'")

        return r

class BoolExpr(Expr):
    def __init__(self, loc, val):
        super(BoolExpr, self).__init__(loc)
        self.val = val

    def __str__(self): return "true" if self.val == True else "false"

    def check(self, sema):
        self.type = Tag.K_bool
        return self.type

class IdExpr(Expr):
    def __init__(self, loc, id):
        super(IdExpr, self).__init__(loc)
        self.id = id

    def __str__(self): return f"{self.id}"

    def check(self, sema):
        if (assign_stmt := sema.find(self.id)) != None:
            self.type = assign_stmt.type
            return self.type
        return None

class LitExpr(Expr):
    def __init__(self, loc, lit):
        super(LitExpr, self).__init__(loc)
        self.lit = lit

    def __str__(self): return f"{self.lit}"

    def check(self, sema):
        self.type = Tag.K_int
        return self.type
