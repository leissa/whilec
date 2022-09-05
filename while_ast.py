from tok import *

class Tab:
    def __init__(self, ind=0, tab = "\t"):
        self.ind = ind
        self.tab = tab

    def indent(self): self.ind += 1
    def dedent(self): self.ind -= 1
    def __str__(self):
        res = ""
        for i in range(0, self.ind):
            res += self.tab
        return res

tab = Tab()

class AST:
    def __init__(self, loc): self.loc = loc

class Prog(AST):
    def __init__(self, loc, stmt, ret):
        super(Prog, self).__init__(loc)
        self.stmt = stmt
        self.ret  = ret

    def __str__(self):
        head = f"{self.stmt}"
        tail = f"return {self.ret}"
        return head + tail

class Type(AST):
    def __init__(self, loc, tag):
        super(Type, self).__init__(loc)
        self.tag = tag

    def __str__(self): return "bool" if self.tag is Tag.K_bool else "int"

# Stmt

class Stmt(AST):
    def __init__(self, loc): super(Stmt, self).__init__(loc)

class AssignStmt(Stmt):
    def __init__(self, loc, id, type, expr):
        super(AssignStmt, self).__init__(loc)
        self.id   = id
        self.type = type
        self.expr = expr

    def __str__(self):
        return f"{tab}{self.id}: {self.type} = {self.expr}"

class PassStmt(Stmt):
    def __init__(self, loc):
        super(PassStmt, self).__init__(loc)

    def __str__(self): return f"pass"

class SeqStmt(Stmt):
    def __init__(self, loc, s1, s2):
        super(SeqStmt, self).__init__(loc)
        self.s1 = s1
        self.s2 = s2

    def __str__(self): return f"{tab}{self.s1};\n{self.s2}"

class WhileStmt(Stmt):
    def __init__(self, loc, cond, body):
        super(WhileStmt, self).__init__(loc)
        self.cond = cond
        self.body = body

    def __str__(self):
        head = f"while {self.cond} {{\n"
        tab.indent()
        body = f"{self.body}\n"
        tab.dedent()
        tail = f"}}\n"
        return head + body + tail

# Expr

class Expr(AST):
    def __init__(self, loc): super(Expr, self).__init__(loc)

class IdExpr(Expr):
    def __init__(self, loc, id):
        super(IdExpr, self).__init__(loc)
        self.id = id

    def __str__(self): return f"{self.id}"

class LitExpr(Expr):
    def __init__(self, loc, lit):
        super(LitExpr, self).__init__(loc)
        self.lit = lit

    def __str__(self): return f"{self.lit}"

class BinExpr(Expr):
    def __init__(self, loc, lhs, op, rhs):
        super(BinExpr, self).__init__(loc)
        self.lhs = lhs
        self.op  = op
        self.rhs = rhs

    def __str__(self): return f"({self.lhs} {self.op} {self.rhs})"

# Bool

class LitBool(Expr):
    def __init__(self, loc, lit):
        super(LitExpr, self).__init__(loc)
        self.lit = lit

    def __str__(self):
        if self.type is T_bool: return "true" if self.lit == 0 else "false"
        return f'{self.lit}'
