"""
Parses a stream of tokens generated by the lexer.
"""

from enum import IntEnum, auto

from while_ast import Prog,                                 \
    DeclStmt, AssignStmt, StmtList, WhileStmt,              \
    BinExpr, UnaryExpr, BoolExpr, LitExpr, SymExpr, ErrExpr
from lexer import Lexer
from tok import Tag, Tok
from loc import Loc
from err import err

class Prec(IntEnum):
    BOT   = auto()
    OR    = auto()
    AND   = auto()
    NOT   = auto()
    REL   = auto()
    ADD   = auto()
    MUL   = auto()
    UNARY = auto()

class Parser:
    def __init__(self, file):
        self.lexer = Lexer(file)
        self.ahead = self.lexer.lex()
        self.prev  = None

        self.prec = {
            Tag.K_OR : [Prec.OR , Prec.AND],
            Tag.K_AND: [Prec.AND, Prec.NOT],
            Tag.T_EQ : [Prec.REL, Prec.ADD],
            Tag.T_NE : [Prec.REL, Prec.ADD],
            Tag.T_LT : [Prec.REL, Prec.ADD],
            Tag.T_LE : [Prec.REL, Prec.ADD],
            Tag.T_GT : [Prec.REL, Prec.ADD],
            Tag.T_GE : [Prec.REL, Prec.ADD],
            Tag.T_ADD: [Prec.ADD, Prec.MUL],
            Tag.T_SUB: [Prec.ADD, Prec.MUL],
            Tag.T_MUL: [Prec.MUL, Prec.UNARY],
        }

    # helpers to track loc

    class Tracker:
        def __init__(self, begin, parser):
            self.begin  = begin
            self.parser = parser

        def loc(self):
            return Loc(self.parser.ahead.loc.file, self.begin, self.parser.prev)

    def track(self):
        return self.Tracker(self.ahead.loc.begin, self)

    # helpers get next Tok from Lexer

    def lex(self):
        result     = self.ahead
        self.prev  = result.loc.begin
        self.ahead = self.lexer.lex()
        return result

    def accept(self, tag):
        return self.lex() if self.ahead.isa(tag) else None

    def eat(self, tag):
        assert self.ahead.isa(tag)
        return self.lex()

    def err(self, expected = None, got = None, ctxt = None):
        if ctxt is None:
            self.err(expected, self.ahead, got)
        else:
            err(got.loc, f"expected {expected}, got '{got}' while parsing {ctxt}")

    def expect(self, tag, ctxt):
        if self.ahead.isa(tag): return self.lex()
        self.err(f"'{tag}'", ctxt)
        return None

    # entry

    def parse_prog(self):
        t    = self.track()
        stmt = self.parse_stmt()
        self.expect(Tag.K_RETURN, "program")
        ret  = self.parse_expr("return expression")
        self.expect(Tag.T_SEMICOLON, "at the end of the final return of the program")
        self.expect(Tag.M_EOF, "at the end of the program")
        return Prog(t.loc(), stmt, ret)

    def parse_sym(self, ctxt=None):
        if (tok := self.accept(Tag.M_SYM)) is not None: return tok
        if ctxt is not None:
            self.err("identifier", ctxt)
            return Tok(self.ahead.loc, "<error>")
        return None

    # Stmt

    def parse_stmt(self):
        t     = self.track()
        stmts = []

        while True:
            while self.accept(Tag.T_SEMICOLON):
                pass

            if self.ahead.isa(Tag.K_INT) or self.ahead.isa(Tag.K_BOOL):
                stmts.append(self.parse_decl_stmt())
            elif self.ahead.isa(Tag.M_SYM):
                stmts.append(self.parse_assign_stmt())
            elif self.ahead.isa(Tag.K_WHILE):
                stmts.append(self.parse_while_stmt())
            else:
                break

        return StmtList(t.loc(), stmts)

    def parse_assign_stmt(self):
        t    = self.track()
        sym  = self.eat(Tag.M_SYM)
        self.expect(Tag.T_ASSIGN, "assignment statement")
        expr = self.parse_expr("right-hand side of an assignment statement")
        self.expect(Tag.T_SEMICOLON, "end of an assignment statement")
        return AssignStmt(t.loc(), sym, expr)

    def parse_decl_stmt(self):
        t    = self.track()
        ty   = self.lex().tag
        sym  = self.parse_sym("identifier of a declaration statement")
        self.expect(Tag.T_ASSIGN, "declaration statement")
        expr = self.parse_expr("right-hand side of a declaration statement")
        self.expect(Tag.T_SEMICOLON, "end of a declaration statement")
        return DeclStmt(t.loc(), ty, sym, expr)

    def parse_while_stmt(self):
        t    = self.track()
        self.eat(Tag.K_WHILE)
        cond = self.parse_expr("condition of a while statement")
        self.expect(Tag.D_BRACE_L, "while statement")
        body = self.parse_stmt()
        self.expect(Tag.D_BRACE_R, "while statement")
        return WhileStmt(t.loc(), cond, body)

    # Expr

    def parse_expr(self, ctxt = None, cur_prec = Prec.BOT):
        t   = self.track()
        lhs = self.parse_primary_or_unary_expr(ctxt)

        while self.ahead.is_bin_op():
            (l_prec, r_prec) = self.prec[self.ahead.tag]
            if l_prec < cur_prec:
                break
            op  = self.lex().tag
            rhs = self.parse_expr("right-hand side of operator '{op}'", r_prec)
            lhs = BinExpr(t.loc(), lhs, op, rhs)

        return lhs

    def parse_primary_or_unary_expr(self, ctxt):
        t = self.track()

        if (tok := self.accept(Tag.K_FALSE)) is not None: return BoolExpr(tok.loc, False  )
        if (tok := self.accept(Tag.K_TRUE )) is not None: return BoolExpr(tok.loc, True   )
        if (tok := self.accept(Tag.M_SYM  )) is not None: return SymExpr (tok.loc, tok    )
        if (tok := self.accept(Tag.M_LIT  )) is not None: return LitExpr (tok.loc, tok.val)

        if self.ahead.tag.is_unary():
            op  = self.lex().tag
            rhs = self.parse_expr("unary expression", Prec.NOT if op is Tag.K_NOT else Prec.UNARY)
            return UnaryExpr(t.loc(), op, rhs)

        if self.accept(Tag.D_PAREN_L):
            expr = self.parse_expr()
            self.expect(Tag.D_PAREN_R, "parenthesized expression")
            return expr

        if ctxt is not None:
            self.err("primary or unary expression", ctxt)
            return ErrExpr(self.ahead.loc)
        assert False
