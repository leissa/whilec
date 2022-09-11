from enum import Enum, auto
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
    While = auto()
    C     = auto()
    Py    = auto()

tab  = Tab()
emit = Emit.While

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
        res = ""

        if emit is Emit.C:
            res += f"#include <stdbool.h>\n"
            res += f"#include <stdio.h>\n"
            res += f"\n"
            res += f"int main() {{\n"
            tab.indent()

        res += f"{self.stmt}"

        if emit is Emit.While:
            res += f"{tab}return {self.ret};\n"
        elif emit is Emit.C:
            if self.ret.type == Tag.K_bool:
                res += f'{tab}printf({self.ret} ? "true\\n" : "false\\n");'
            else:
                res += f'{tab}printf("%i\\n", {self.ret});'
        elif emit is Emit.Py:
            res += f'{tab}print("true" if {self.ret} else "false")\n'

        if emit is Emit.C:
            tab.dedent()
            res += f"\n}}\n"
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

class Stmt(AST):
    def __init__(self, loc): super(Stmt, self).__init__(loc)

class DeclStmt(Stmt):
    def __init__(self, loc, type, id, init):
        super(DeclStmt, self).__init__(loc)
        self.type = type
        self.id   = id
        self.init = init

    def __str__(self):
        if emit is Emit.While: return f"{self.type} {self.id} = {self.init};"
        if emit is Emit.C:     return f"{self.type} _{self.id} = {self.init};"
        if emit is Emit.Py:    return f"_{self.id} = {self.init}"

    def check(self, sema):
        self.init.check(sema)
        sema.bind(self.id, self)

    def eval(self, env):
        val = self.init.eval(env)
        env[self.id.id] = val

class AssignStmt(Stmt):
    def __init__(self, loc, id, init):
        super(AssignStmt, self).__init__(loc)
        self.id   = id
        self.init = init

    def __str__(self):
        if emit is Emit.While: return f"{self.id} = {self.init};"
        if emit is Emit.C:     return f"_{self.id} = {self.init};"
        if emit is Emit.Py:    return f"_{self.id} = {self.init}"

    def check(self, sema):
        self.init.check(sema)
        sema.find(self.id)

    def eval(self, env):
        val = self.init.eval(env)
        env[self.id.id] = val

class StmtList(Stmt):
    def __init__(self, loc, stmts):
        super(StmtList, self).__init__(loc)
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
        super(WhileStmt, self).__init__(loc)
        self.cond = cond
        self.body = body

    def __str__(self):
        if emit is Emit.While:
            head = f"while {self.cond} {{\n"
        elif emit is Emit.C:
            head = f"while ({self.cond}) {{\n"
        else:
            head = f"while {self.cond}:\n"

        tab.indent()
        body = f"{self.body}"
        tab.dedent()
        tail = "" if emit is Emit.Py else f"{tab}}}"
        return head + body + tail

    def check(self, sema):
        self.cond.check(sema)
        self.body.check(sema)

    def eval(self, env):
        while True:
            if (val := self.cond.eval(env)) == False: break
            self.body.eval(env)

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

        op = str(self.op)
        if emit is Emit.C:
            if self.op is Tag.K_and:
                op = "&"
            elif self.op is Tag.K_and:
                op = "|"

        if t != None and t is not x: err(self.lhs.loc,  f"left-hand side of operator '{self.op}' must be of type '{x}' but is of type '{t}'")
        if u != None and u is not x: err(self.rhs.loc, f"right-hand side of operator '{self.op}' must be of type '{x}' but is of type '{u}'")

        return r

    def eval(self, env):
        l = self.lhs.eval(env)
        r = self.rhs.eval(env)
        if self.op is Tag.T_add: return l +  r
        if self.op is Tag.T_sub: return l -  r
        if self.op is Tag.T_mul: return l *  r
        if self.op is Tag.K_and: return l &  r
        if self.op is Tag.K_or : return l |  r
        if self.op is Tag.T_eq : return l == r
        if self.op is Tag.T_ne : return l != r
        if self.op is Tag.T_lt : return l <  r
        if self.op is Tag.T_le : return l <= r
        if self.op is Tag.T_gt : return l >  r
        if self.op is Tag.T_ge : return l >= r
        assert False

class UnaryExpr(Expr):
    def __init__(self, loc, op, rhs):
        super(UnaryExpr, self).__init__(loc)
        self.op  = op
        self.rhs = rhs

    def __str__(self):
        op = self.op
        if emit is Emit.C and self.op is Tag.K_not: op = "!"
        return f"({op} {self.rhs})"

    def check(self, sema):
        u = self.rhs.check(sema)

        if self.op is Tag.K_not:
            x = Tag.K_bool
            r = Tag.K_bool
        else:
            x = Tag.K_int
            r = Tag.K_int

        op = str(self.op)

        if u != None and u is not x:
            err(self.rhs.loc, f"right-hand side of operator '{self.op}' must be of type '{x}' but is of type '{u}'")

        return r

    def eval(self, env):
        r = self.rhs.eval(env)
        if self.op is Tag.K_not: return not r
        if self.op is Tag.T_add: return     r
        if self.op is Tag.T_sub: return -   r
        assert False

class BoolExpr(Expr):
    def __init__(self, loc, val):
        super(BoolExpr, self).__init__(loc)
        self.val = val

    def __str__(self):
        if emit is Emit.Py:
            return "True" if self.val else "False"
        else:
            return "true" if self.val else "false"

    def check(self, sema):
        self.type = Tag.K_bool
        return self.type

    def eval(self, env): return self.val

class IdExpr(Expr):
    def __init__(self, loc, id):
        super(IdExpr, self).__init__(loc)
        self.id = id

    def __str__(self):
        prefix = "" if emit is Emit.While else "_"
        return f"{prefix}{self.id}"

    def check(self, sema):
        if (decl := sema.find(self.id)) != None:
            self.decl = decl
            self.type = decl.type
            return self.type
        return None

    def eval(self, env): return env[self.id.id]

class LitExpr(Expr):
    def __init__(self, loc, val):
        super(LitExpr, self).__init__(loc)
        self.val = val

    def __str__(self): return f"{self.val}"

    def check(self, sema):
        self.type = Tag.K_int
        return self.type

    def eval(self, env): return self.val

class ErrExpr(Expr):
    def __init__(self, loc): super(ErrExpr, self).__init__(loc)
    def __str__(self): return f"<error>"
    def check(self, sema): return None
