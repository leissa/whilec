from lexer import *

class Parser:
    def __init__(self, filename):
        self.lexer = Lexer(filename)
        self.lex()

    def lex(self):
        self.ahead = self.lexer.lex()

    def accept(self, tag):
        if self.ahead is not tag:
            return None
        return lex()

    def eat(self, tag):
        assert self.ahead is tag
        return lex()

    def expect(self, tag): # TODO
        assert self.ahead is tag
        return lex()

    def parse_stmnt(self):
        if self.ahead is Tok.Tag.M_id:
            return self.parse_assign_stmnt()
        if self.ahead is Tok.Tag.K_while:
            return self.parse_while_stmt()

    def parse_assign_stmnt():
        id = self.eat(Tok.Tag.M_id).id

    def parse_expr(self):
        lhs = self.parse_primary_expr()
        op  = lex()
        rhs = self.parse_expr()
        return BinExpr(lhs, op, rhs)

    def parse_primary_expr(self):
        if self.ahead is Tok.Tag.M_id:
            return IdExpr(lex().sym)
        if self.ahead is Tok.Tag.M_lit:
            return LitExpr(lex().val)
        if self.ahead is Tok.Tag.D_paren_l:
            expr = self.parse_expr()
            expect(Tok.Tag.D_paren_r)
            return expr
