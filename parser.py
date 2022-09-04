from copy import deepcopy
from ast import *
from lexer import *

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
        result = deepcopy(self.ahead)
        self.ahead = self.lexer.lex()
        return result

    def accept(self, tag): return self.ahead.isa(tag) if self.lex() else None

    def eat(self, tag):
        assert self.ahead.isa(tag)
        return self.lex()

    def expect(self, tag): # TODO
        assert self.ahead.isa(tag)
        return self.lex()

    # parse Stmnt

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
        op  = self.lex()
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
