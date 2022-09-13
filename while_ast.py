"""
The While AST (Abstract Syntax Tree)
"""

from enum import Enum, auto
from tok import Tag
from err import err

class Tab:
    def __init__(self, tab = "\t"):
        self.ind = 0
        self.tab = tab

    def indent(self):
        self.ind += 1

    def dedent(self):
        self.ind -= 1

    def __str__(self):
        res = ""
        for _ in range(self.ind):
            res += self.tab
        return res

class Sema:
    def __init__(self):
        self.scope = {}

    def find(self, tok):
        if tok.is_error(): return None
        if tok.id in self.scope: return self.scope[tok.id]
        err(tok.loc, f"identifier '{tok}' not found")
        return None

    def bind(self, tok, decl):
        if tok.is_error(): return True
        if tok.id in self.scope:
            err(tok.loc, f"identifier '{tok}' already declared here: {self.scope[tok.id].loc}")
            return False

        self.scope[tok.id] = decl
        return True

class Emit(Enum):
    WHILE = auto()
    C     = auto()
    PY    = auto()

tab  = Tab()
emit = Emit.WHILE

# AST

class AST:
    def __init__(self, loc):
        self.loc = loc

class Prog(AST):
    def __init__(self, loc, stmt, ret):
        super().__init__(loc)
        self.stmt = stmt
        self.ret  = ret

    def __str__(self):
        res = ""

        if emit is Emit.C:
            res += "#include <stdbool.h>\n"
            res += "#include <stdio.h>\n"
            res += "\n"
            res += "int main() {\n"
            tab.indent()

        res += f"{self.stmt}"

        if emit is Emit.WHILE:
            res += f"{tab}return {self.ret};\n"
        elif emit is Emit.C:
            if self.ret.ty == Tag.K_BOOL:
                res += f'{tab}printf({self.ret} ? "true\\n" : "false\\n");'
            else:
                res += f'{tab}printf("%i\\n", {self.ret});'
        elif emit is Emit.PY:
            res += f'{tab}print("true" if {self.ret} else "false")\n'

        if emit is Emit.C:
            tab.dedent()
            res += "\n}\n"
        return res

    def check(self):
        sema = Sema()
        self.stmt.check(sema)
        self.ret.check(sema)

    def eval(self):
        env = {}
        self.stmt.eval(env)
        print(self.ret.eval(env))

# Stmt

class Stmt(AST): pass

class DeclStmt(Stmt):
    def __init__(self, loc, ty, id, init):
        super().__init__(loc)
        self.ty   = ty
        self.id   = id
        self.init = init

    def __str__(self):
        if emit is Emit.WHILE: return f"{self.ty} {self.id} = {self.init};"
        if emit is Emit.C:     return f"{self.ty} _{self.id} = {self.init};"
        if emit is Emit.PY:    return f"_{self.id} = {self.init}"
        assert False

    def check(self, sema):
        self.init.check(sema)
        sema.bind(self.id, self)

    def eval(self, env):
        val = self.init.eval(env)
        env[self.id.id] = val

class AssignStmt(Stmt):
    def __init__(self, loc, id, init):
        super().__init__(loc)
        self.id   = id
        self.init = init

    def __str__(self):
        if emit is Emit.WHILE: return f"{self.id} = {self.init};"
        if emit is Emit.C:     return f"_{self.id} = {self.init};"
        if emit is Emit.PY:    return f"_{self.id} = {self.init}"

    def check(self, sema):
        self.init.check(sema)
        sema.find(self.id)

    def eval(self, env):
        val = self.init.eval(env)
        env[self.id.id] = val

class StmtList(Stmt):
    def __init__(self, loc, stmts):
        super().__init__(loc)
        self.stmts = stmts

    def __str__(self):
        res = ""
        for stmt in self.stmts:
            res += f"{tab}{stmt}\n"
        return res

    def check(self, sema):
        for stmt in self.stmts: stmt.check(sema)

    def eval(self, env):
        for stmt in self.stmts: stmt.eval(env)

class WhileStmt(Stmt):
    def __init__(self, loc, cond, body):
        super().__init__(loc)
        self.cond = cond
        self.body = body

    def __str__(self):
        if emit is Emit.WHILE:
            head = f"while {self.cond} {{\n"
        elif emit is Emit.C:
            head = f"while ({self.cond}) {{\n"
        else:
            head = f"while {self.cond}:\n"

        tab.indent()
        body = f"{self.body}"
        tab.dedent()
        tail = "" if emit is Emit.PY else f"{tab}}}"
        return head + body + tail

    def check(self, sema):
        self.cond.check(sema)
        self.body.check(sema)

    def eval(self, env):
        while True:
            if not self.cond.eval(env): break
            self.body.eval(env)

# Expr

class Expr(AST):
    def __init__(self, loc):
        super().__init__(loc)
        self.ty = None

class BinExpr(Expr):
    def __init__(self, loc, lhs, op, rhs):
        super().__init__(loc)
        self.lhs = lhs
        self.op  = op
        self.rhs = rhs

    def __str__(self): return f"({self.lhs} {self.op} {self.rhs})"

    def check(self, sema):
        t  = self.lhs.check(sema)
        u  = self.rhs.check(sema)
        op = str(self.op)

        if self.op.is_arith():
            x = Tag.K_INT
            r = Tag.K_INT
        elif self.op.is_rel():
            x = Tag.K_INT
            r = Tag.K_BOOL
        elif self.op.is_logic():
            x = Tag.K_BOOL
            r = Tag.K_BOOL
        else:
            assert False

        if emit is Emit.C:
            if self.op is Tag.K_AND:
                op = "&"
            elif self.op is Tag.K_AND:
                op = "|"

        if t is not None and t is not x:
            err(self.lhs.loc,  f"left-hand side of operator '{op}' must be of type '{x}' but is of type '{t}'")
        if u is not None and u is not x:
            err(self.rhs.loc, f"right-hand side of operator '{op}' must be of type '{x}' but is of type '{u}'")

        return r

    def eval(self, env):
        l = self.lhs.eval(env)
        r = self.rhs.eval(env)
        if self.op is Tag.T_ADD: return l +  r
        if self.op is Tag.T_SUB: return l -  r
        if self.op is Tag.T_MUL: return l *  r
        if self.op is Tag.K_AND: return l &  r
        if self.op is Tag.K_OR : return l |  r
        if self.op is Tag.T_EQ : return l == r
        if self.op is Tag.T_NE : return l != r
        if self.op is Tag.T_LT : return l <  r
        if self.op is Tag.T_LE : return l <= r
        if self.op is Tag.T_GT : return l >  r
        if self.op is Tag.T_GE : return l >= r
        assert False

class UnaryExpr(Expr):
    def __init__(self, loc, op, rhs):
        super().__init__(loc)
        self.op  = op
        self.rhs = rhs

    def __str__(self):
        op = self.op
        if emit is Emit.C and self.op is Tag.K_NOT: op = "!"
        return f"{op}({self.rhs})"

    def check(self, sema):
        u  = self.rhs.check(sema)
        op = str(self.op)

        if self.op is Tag.K_NOT:
            x = Tag.K_BOOL
            r = Tag.K_BOOL
        else:
            x = Tag.K_INT
            r = Tag.K_INT

        if u is not None and u is not x:
            err(self.rhs.loc, f"operand of operator '{self.op}' must be of type '{x}' but is of type '{u}'")

        return r

    def eval(self, env):
        r = self.rhs.eval(env)
        if self.op is Tag.K_NOT: return not r
        if self.op is Tag.T_ADD: return     r
        if self.op is Tag.T_SUB: return -   r
        assert False

class BoolExpr(Expr):
    def __init__(self, loc, val):
        super().__init__(loc)
        self.val = val

    def __str__(self):
        if emit is Emit.PY: return "True" if self.val else "False"
        return "true" if self.val else "false"

    def check(self, sema):
        self.ty = Tag.K_BOOL
        return self.ty

    def eval(self, env): return self.val

class IdExpr(Expr):
    def __init__(self, loc, id):
        super().__init__(loc)
        self.id = id

    def __str__(self):
        prefix = "" if emit is Emit.WHILE else "_"
        return f"{prefix}{self.id}"

    def check(self, sema):
        if (decl := sema.find(self.id)) is not None:
            self.decl = decl
            self.ty   = decl.ty
            return self.ty
        return None

    def eval(self, env): return env[self.id.id]

class LitExpr(Expr):
    def __init__(self, loc, val):
        super().__init__(loc)
        self.val = val

    def __str__(self): return f"{self.val}"

    def check(self, sema):
        self.ty = Tag.K_INT
        return self.ty

    def eval(self, env): return self.val

class ErrExpr(Expr):
    def __str__(self):
        return "<error>"

    def check(self, _):
        return None
