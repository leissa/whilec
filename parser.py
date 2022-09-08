from copy import deepcopy

from while_ast import *
from lexer import *
from err import *

class Parser:
    def __init__(self, file):
        self.lexer = Lexer(file)
        self.ahead = self.lexer.lex()
        self.prev  = None

    # helpers to track loc

    class Tracker:
        def __init__(self, begin, parser):
            self.begin  = begin
            self.parser = parser

        def loc(self): return Loc(self.parser.ahead.loc.file, self.begin, self.parser.prev)

    def track(self): return self.Tracker(self.ahead.loc.begin, self)

    # helpers get next Tok from Lexer

    def lex(self):
        result     = self.ahead
        self.prev  = result.loc.begin
        self.ahead = self.lexer.lex()
        return result

    def accept(self, tag): return self.lex() if self.ahead.isa(tag) else None

    def eat(self, tag):
        assert self.ahead.isa(tag)
        return self.lex()

    def err(self, a = None, b = None, c = None):
        if c == None:
            self.err(a, self.ahead, b)
        else:
            err(b.loc, f"expected {a}, got '{b}' while parsing {c}")

    def expect(self, tag, ctxt):
        if self.ahead.isa(tag): return self.lex()
        self.err(f"'{tag}'", ctxt)
        return None;

    def parse_prog(self):
        t    = self.track()
        stmt = self.parse_stmt()
        self.expect(Tag.K_return, "program")
        ret  = self.parse_expr("return expression")
        self.expect(Tag.T_semicolon, "at the end of the final return of the program")
        self.expect(Tag.M_eof, "at the end of the program")
        return Prog(t.loc(), stmt, ret)

    def parse_id(self, ctxt=None):
        if (tok := self.accept(Tag.M_id)) != None: return tok
        if ctxt != None:
            self.err("identifier", ctxt)
            return Tok(self.ahead.loc, "<error>")
        return None

    # Stmt

    def parse_stmt(self, ctxt=None):
        t     = self.track();
        stmts = []

        while True:
            while self.accept(Tag.T_semicolon): pass

            if self.ahead.isa(Tag.K_int) or self.ahead.isa(Tag.K_bool):
                stmts.append(self.parse_decl_stmt())
            elif self.ahead.isa(Tag.M_id):
                stmts.append(self.parse_assign_stmt())
            elif self.ahead.isa(Tag.K_while):
                stmts.append(self.parse_while_stmt())
            else:
                break

        if not stmts and ctxt != None:
            self.err("statement", ctxt)

        return StmtList(t.loc(), stmts)

    def parse_assign_stmt(self):
        t    = self.track()
        id   = self.eat(Tag.M_id)
        self.expect(Tag.T_assign, "assignment statement")
        expr = self.parse_expr("right-hand side of an assignment statement")
        self.expect(Tag.T_semicolon, "end of an assignment statement")
        return AssignStmt(t.loc(), id, expr)

    def parse_decl_stmt(self):
        t    = self.track()
        type = self.lex().tag
        id   = self.parse_id("identifier of a declaration statement")
        self.expect(Tag.T_assign, "declaration statement")
        expr = self.parse_expr("right-hand side of a declaration statement")
        self.expect(Tag.T_semicolon, "end of a declaration statement")
        return DeclStmt(t.loc(), type, id, expr)

    def parse_while_stmt(self):
        t    = self.track()
        self.eat(Tag.K_while)
        cond = self.parse_expr("condition of a while statement")
        self.expect(Tag.D_brace_l, "while statement")
        body = self.parse_stmt("body of a while statement")
        self.expect(Tag.D_brace_r, "while statement")
        return WhileStmt(t.loc(), cond, body)

    # Expr

    def parse_expr(self, ctxt=None):
        t   = self.track()
        lhs = self.parse_primary_expr(ctxt)

        while self.ahead.is_bin_op():
            op  = self.lex().tag
            rhs = self.parse_expr()
            lhs = BinExpr(t.loc(), lhs, op, rhs)

        return lhs

    def parse_primary_expr(self, ctxt):
        if (tok := self.accept(Tag.K_false)) != None: return BoolExpr(tok.loc, False  )
        if (tok := self.accept(Tag.K_true )) != None: return BoolExpr(tok.loc, True   )
        if (tok := self.accept(Tag.M_id   )) != None: return IdExpr  (tok.loc, tok    )
        if (tok := self.accept(Tag.M_lit  )) != None: return LitExpr (tok.loc, tok.val)
        if self.accept(Tag.D_paren_l):
            expr = self.parse_expr()
            self.expect(Tag.D_paren_r, "parenthesized expression")
            return expr

        if ctxt != None:
            self.err("primary expression", ctxt)
            return ErrExpr(self.ahead.loc)
        assert False
