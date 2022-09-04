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
        def __init__(self, loc): self.loc_ = deepcopy(loc)
        def loc(self): return self.loc_

    def track(self): return self.Tracker(self.prev)

    # helpers get next Tok from Lexer

    def lex(self):
        self.prev  = self.ahead.loc
        result     = self.ahead
        self.ahead = self.lexer.lex()
        return result

    def accept(self, tag): return self.ahead.isa(tag) if self.lex() else None

    def eat(self, tag):
        assert self.ahead.isa(tag)
        return self.lex()

    def xerr(self, a = None, b = None, c = None):
        if c == None:
            self.xerr(a, self.ahead, b)
        else:
            err.err(tok.loc(), "expected {what}, got '{tok}' while parsing {ctxt}")

    def expect(self, tag, ctxt):
        if self.ahead.isa(tag): return self.lex()
        self.xerr(f"'{tag}'", ctxt)
        return None;

    def parse_prog(self):
        stmnt = self.parse_stmnt()
        self.expect(Tag.M_eof, 'program' )
        return stmnt

    def parse_stmnt(self):
        if self.ahead.isa(Tag.M_id):    return self.parse_assign_stmnt()
        if self.ahead.isa(Tag.K_while): return self.parse_while_stmt()

    def parse_assign_stmnt(self):
        t    = self.track()
        id   = self.eat(Tag.M_id).id
        self.eat(Tag.T_assign)
        expr = self.parse_expr()
        self.expect(Tag.T_semicolon)
        return AssignStmt(t.loc(), id, expr)

    # parse Expr

    def parse_expr(self):
        t   = self.track()
        lhs = self.parse_primary_expr()
        op  = self.lex().tag
        rhs = self.parse_expr()
        return BinExpr(t.loc(), lhs, op, rhs)

    def parse_primary_expr(self):
        t = self.track()
        if self.ahead.isa(Tag.M_id ): return IdExpr (t.loc(), self.lex().id )
        if self.ahead.isa(Tag.M_lit): return LitExpr(t.loc(), self.lex().lit)
        if self.ahead.isa(Tag.D_paren_l):
            self.eat(Tag.D_paren_l)
            expr = self.parse_expr()
            self.expect(Tag.D_paren_r)
            return expr

    # parse Bool
