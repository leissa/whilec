"""
The While AST (Abstract Syntax Tree)
"""

from enum import Enum, auto
from tok import Tag
from err import err, note

def same(t, u):
    return t is None or u is None or t == u

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
        self.scopes = []
        self.push() # root scope

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def find(self, tok):
        if tok.is_error(): return None

        for scope in reversed(self.scopes):
            if tok.sym in scope:
                return scope[tok.sym]

        err(tok.loc, f"identifier '{tok}' not found")
        return None

    def bind(self, tok, decl):
        if tok.is_error():
            return True

        curr_scope = self.scopes[-1]

        if tok.sym in curr_scope:
            prev = curr_scope[tok.sym]
            err(decl.loc, f"redeclaration of '{tok}' in the same scope")
            note(prev.loc, "previous declaration here")
            return False

        curr_scope[tok.sym] = decl
        return True

class Emit(Enum):
    EVAL  = auto()
    WHILE = auto()
    C     = auto()
    PY    = auto()

TAB  = Tab()
EMIT = Emit.WHILE

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

        if EMIT is Emit.C:
            res += "#include <stdbool.h>\n"
            res += "#include <stdio.h>\n"
            res += "\n"
            res += "int main() {\n"
            TAB.indent()

        res += f"{self.stmt}"

        if EMIT is Emit.WHILE:
            res += f"{TAB}return {self.ret};\n"
        elif EMIT is Emit.C:
            if self.ret.ty == Tag.K_BOOL:
                res += f'{TAB}printf({self.ret} ? "true\\n" : "false\\n");'
            else:
                res += f'{TAB}printf("%i\\n", {self.ret});'
        elif EMIT is Emit.PY:
            if self.ret.ty is Tag.K_BOOL:
                res += f'{TAB}print("true" if {self.ret} else "false")\n'
            else:
                res += f'{TAB}print({self.ret})'

        if EMIT is Emit.C:
            TAB.dedent()
            res += "\n}\n"
        return res

    def check(self):
        sema = Sema()
        self.stmt.check(sema)
        self.ret.check(sema)

    def eval(self):
        assert EMIT is Emit.EVAL
        env = {}
        self.stmt.eval(env)
        print(self.ret.eval(env))

# Stmt

class Stmt(AST): pass

DECL_COUNTER = 0

def name(decl, sym = None):
    if decl is None:                         return f"{sym}"
    if EMIT is Emit.WHILE:                   return f"{decl.sym}"
    if EMIT is Emit.C:                       return f"_{decl.sym}"
    if EMIT is Emit.EVAL or EMIT is Emit.PY: return f"{decl.sym}_{decl.counter}"
    assert False

class DeclStmt(Stmt):
    def __init__(self, loc, ty, sym, init):
        global DECL_COUNTER
        super().__init__(loc)
        self.ty   = ty
        self.sym  = sym
        self.init = init
        self.counter = DECL_COUNTER
        DECL_COUNTER += 1

    def __str__(self):
        if EMIT is Emit.PY: return f"{name(self)} = {self.init}"
        return f"{self.ty} {name(self)} = {self.init};"

    def check(self, sema):
        init_ty = self.init.check(sema)
        if not same(init_ty, self.ty):
            err(self.loc, f"initialization of declaration statement is of type '{init_ty}' but '{self.sym}' is declared of type '{self.ty}'")
        sema.bind(self.sym, self)

    def eval(self, env):
        val = self.init.eval(env)
        env[name(self)] = val

class AssignStmt(Stmt):
    def __init__(self, loc, sym, init):
        super().__init__(loc)
        self.sym  = sym
        self.init = init
        self.decl = None

    def __str__(self):
        if EMIT is Emit.PY:
            return f"{name(self.decl, self.sym)} = {self.init}"
        return f"{name(self.decl, self.sym)} = {self.init};"

    def check(self, sema):
        init_ty = self.init.check(sema)
        self.decl = sema.find(self.sym)
        if not same(init_ty, self.decl.ty):
            err(self.loc, f"right-hand side of asssignment statement is of type '{init_ty}' but '{self.decl.sym}' is declared of type '{self.decl.ty}'")
            note(self.decl.loc, "previous declaration here")

    def eval(self, env):
        val = self.init.eval(env)
        env[name(self.decl)] = val

class StmtList(Stmt):
    def __init__(self, loc, stmts):
        super().__init__(loc)
        self.stmts = stmts

    def __str__(self):
        res = ""
        for stmt in self.stmts:
            res += f"{TAB}{stmt}\n"
        return res

    def check(self, sema):
        for stmt in self.stmts:
            stmt.check(sema)

    def eval(self, env):
        for stmt in self.stmts:
            stmt.eval(env)

class WhileStmt(Stmt):
    def __init__(self, loc, cond, body):
        super().__init__(loc)
        self.cond = cond
        self.body = body

    def __str__(self):
        if EMIT is Emit.WHILE:
            head = f"while {self.cond} {{\n"
        elif EMIT is Emit.C:
            head = f"while ({self.cond}) {{\n"
        else:
            head = f"while {self.cond}:\n"

        TAB.indent()
        body = f"{self.body}"
        TAB.dedent()
        tail = "" if EMIT is Emit.PY else f"{TAB}}}"
        return head + body + tail

    def check(self, sema):
        cond_ty = self.cond.check(sema)
        if not same(cond_ty, Tag.K_BOOL):
            err(self.cond.loc, f"condition of a while statement must be of type `bool` but is of type '{cond_ty}'")

        sema.push()
        self.body.check(sema)
        sema.pop()

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

    def __str__(self):
        op = str(self.op)

        if EMIT is Emit.C:
            if self.op is Tag.K_AND:
                op = "&"
            elif self.op is Tag.K_AND:
                op = "|"

        return f"({self.lhs} {op} {self.rhs})"

    def check(self, sema):
        l_ty  = self.lhs.check(sema)
        r_ty  = self.rhs.check(sema)

        if self.op.is_arith():
            expected_ty = Tag.K_INT
            result_ty   = Tag.K_INT
        elif self.op.is_rel():
            expected_ty = Tag.K_INT
            result_ty   = Tag.K_BOOL
        elif self.op.is_logic():
            expected_ty = Tag.K_BOOL
            result_ty   = Tag.K_BOOL
        else:
            assert False

        if not same(l_ty, expected_ty):
            err(self.lhs.loc, f"left-hand side of operator '{self.op}' must be of type '{expected_ty}' but is of type '{l_ty}'")
        if not same(r_ty, expected_ty):
            err(self.rhs.loc, f"right-hand side of operator '{self.op}' must be of type '{expected_ty}' but is of type '{r_ty}'")

        return result_ty

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
        op = "!" if EMIT is Emit.C and self.op is Tag.K_NOT else str(self.op)
        return f"{op}({self.rhs})"

    def check(self, sema):
        r_ty = self.rhs.check(sema)

        if self.op is Tag.K_NOT:
            expected_ty = Tag.K_BOOL
            result_ty   = Tag.K_BOOL
        else:
            expected_ty = Tag.K_INT
            result_ty   = Tag.K_INT

        if not same(r_ty, expected_ty):
            err(self.rhs.loc, f"operand of operator '{self.op}' must be of type '{expected_ty}' but is of type '{r_ty}'")

        return result_ty

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
        if EMIT is Emit.PY: return "True" if self.val else "False"
        return "true" if self.val else "false"

    def check(self, _):
        self.ty = Tag.K_BOOL
        return self.ty

    def eval(self, _):
        return self.val

class SymExpr(Expr):
    def __init__(self, loc, sym):
        super().__init__(loc)
        self.sym  = sym
        self.decl = None

    def __str__(self):
        return f"{name(self.decl, self.sym)}"

    def check(self, sema):
        if (decl := sema.find(self.sym)) is not None:
            self.decl = decl
            self.ty   = decl.ty
            return self.ty
        return None

    def eval(self, env):
        return env[name(self.decl)]

class LitExpr(Expr):
    def __init__(self, loc, val):
        super().__init__(loc)
        self.val = val

    def __str__(self):
        return f"{self.val}"

    def check(self, _):
        self.ty = Tag.K_INT
        return self.ty

    def eval(self, _):
        return self.val

class ErrExpr(Expr):
    def __str__(self):
        return "<error>"

    def check(self, _):
        return None
