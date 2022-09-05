from copy import deepcopy

from while_ast import *
from lexer import *
from err import *

class Parser:
    def __init__(self, filename):
        self.lexer = Lexer(filename)
        self.ahead = deepcopy(self.lexer.lex())
        self.prev  = self.ahead.loc

    # helpers to track loc

    class Tracker:
        def __init__(self, loc): self.__loc = loc.copy()
        def loc(self): return self.__loc

    def track(self): return self.Tracker(self.prev)

    # helpers get next Tok from Lexer

    def lex(self):
        self.prev  = self.ahead.loc
        result     = self.ahead
        self.ahead = self.lexer.lex()
        return result

    def accept(self, tag): return self.lex() if self.ahead.isa(tag) else None

    def eat(self, tag):
        assert self.ahead.isa(tag)
        return self.lex()

    def xerr(self, a = None, b = None, c = None):
        if c == None:
            self.xerr(a, self.ahead, b)
        else:
            got = str(b) if isinstance(b, Tag) else b
            err(b.loc, f"expected {a}, got '{b}' while parsing {c}")

    def expect(self, tag, ctxt):
        if self.ahead.isa(tag): return self.lex()
        self.xerr(f"'{tag}'", ctxt)
        return None;

    def parse_prog(self):
        t    = self.track()
        stmt = self.parse_stmt()
        self.expect(Tag.K_return, "program")
        ret  = self.parse_expr()
        self.expect(Tag.T_semicolon, "at the end of the final return of the program")
        self.expect(Tag.M_eof, "at the end of the program")
        return Prog(t.loc(), stmt, ret)

    def parse_type(self, ctxt):
        if self.ahead.is_type():
            tok = self.lex()
            return Type(tok.loc, tok.tag)
        self.expect("type", "type")

    def parse_id(self, ctxt=None):
        if (tok := self.accept(Tag.M_id)) != None: return tok
        return None

    # Stmt

    def parse_stmt(self, ctxt=None):
        t     = self.track();
        stmts = []

        while True:
            while self.accept(Tag.T_semicolon): pass

            if self.ahead.isa(Tag.M_id):
                stmts.append(self.parse_assign_stmt())
            elif self.ahead.isa(Tag.K_while):
                stmts.append(self.parse_while_stmt())
            else:
                break

        return StmtList(t.loc(), stmts)

    def parse_assign_stmt(self):
        t    = self.track()
        id   = self.eat(Tag.M_id).id
        self.expect(Tag.T_colon, "type ascription within an assignment statement")
        type = self.parse_type("type ascription within an assignment statement")
        self.expect(Tag.T_assign, "assignment statement")
        expr = self.parse_expr()
        return AssignStmt(t.loc(), id, type, expr)

    def parse_while_stmt(self):
        t    = self.track()
        self.eat(Tag.K_while)
        cond = self.parse_expr("condition of a while statement")
        self.expect(Tag.D_brace_l, "while statement")
        body = self.parse_stmt("body of a while statement")
        self.expect(Tag.D_brace_r, "while statement")
        return WhileStmt(t.loc(), cond, body)

    # Expr

    def parse_expr(self, ctxt = None):
        t   = self.track()
        lhs = self.parse_primary_expr(ctxt)

        if self.ahead.is_bin_op():
            op  = self.lex().tag
            rhs = self.parse_expr()
            return BinExpr(t.loc(), lhs, op, rhs)

        return lhs

    def parse_primary_expr(self, ctxt):
        t = self.track()
        if self.ahead.isa(Tag.M_id ):  return IdExpr (t.loc(), self.lex().id )
        if self.ahead.isa(Tag.M_lit):  return LitExpr(t.loc(), self.lex().lit)
        if self.accept(Tag.K_false):
            lit_expr = LitExpr(t.loc(), 0)
            lit_expr.type = Tag.T_bool
            return lit_expr
        if self.accept(Tag.K_true):
            lit_expr = LitExpr(t.loc(), 1)
            lit_expr.type = Tag.T_bool
            return lit_expr
        if self.ahead.isa(Tag.D_paren_l):
            self.eat(Tag.D_paren_l)
            expr = self.parse_expr()
            self.expect(Tag.D_paren_r)
            return expr
        self.xerr("primary expression", ctxt)
