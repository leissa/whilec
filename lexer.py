from copy import deepcopy
import string

from err import err
from loc import *
from tok import *

class Lexer:
    def __init__(self, filename):
        self.loc = Loc(filename, Pos(1, 1), Pos(1, 1))
        self.peek = Pos(1, 1)
        self.file = open(filename, "r")
        self.keywords = {
            "and":    Tag.K_and,
            "or":     Tag.K_or,
            "not":    Tag.K_not,
            "bool":   Tag.K_bool,
            "int":    Tag.K_int,
            "true":   Tag.K_true,
            "false":  Tag.K_false,
            "pass":   Tag.K_pass,
            "return": Tag.K_return,
            "while":  Tag.K_while,
        }

    def accept_if(self, pred):
        tell = self.file.tell()
        char = self.file.read(1)

        if pred(char):
            self.str += char
            self.loc.finis = deepcopy(self.peek)

            if char == "": # end of file
                pass
            elif char == "\n":
                self.peek.row += 1
                self.peek.col = 1
            else:
                self.peek.col += 1
            return True;

        self.file.seek(tell) # undo read
        return False;

    def eat(self): self.accept_if(lambda _ : True)

    def accept(self, char): return self.accept_if(lambda c : c == char)

    def lex(self):
        while True:
            self.loc.begin = deepcopy(self.peek)
            self.loc.finis = deepcopy(self.peek)
            self.str = ""

            if self.accept("" ): return Tok(self.loc, Tag.M_eof)
            if self.accept_if(lambda char : char in string.whitespace): continue
            if self.accept("{"): return Tok(self.loc, Tag.D_brace_l)
            if self.accept("}"): return Tok(self.loc, Tag.D_brace_r)
            if self.accept("("): return Tok(self.loc, Tag.D_paren_l)
            if self.accept(")"): return Tok(self.loc, Tag.D_paren_r)
            if self.accept("+"): return Tok(self.loc, Tag.T_add)
            if self.accept("-"): return Tok(self.loc, Tag.T_sub)
            if self.accept(";"): return Tok(self.loc, Tag.T_semicolon)

            if self.accept("="):
                if self.accept("="): return Tok(self.loc, Tag.T_eq)
                return Tok(self.loc, Tag.T_assign)

            if self.accept("<"):
                if self.accept("="): return Tok(self.loc, Tag.T_le)
                return Tok(self.loc, Tag.T_lt)

            if self.accept(">"):
                if self.accept("="): return Tok(self.loc, Tag.T_ge)
                return Tok(self.loc, Tag.T_gt)

            if self.accept("!"):
                if self.accept("="): return Tok(self.loc, Tag.T_ne)
                self.eat()
                err(self.loc.anew_begin(), f"invalid input char '{self.str}'; maybe you wanted to use '!='?")
                continue

            # literal
            if self.accept_if(lambda char : char in string.digits):
                while self.accept_if(lambda char : char in string.digits): pass
                return Tok(self.loc, int(self.str))

            # identifier
            if self.accept_if(lambda char : char in string.ascii_letters):
                while self.accept_if(lambda char : char in string.ascii_letters or char in string.digits): pass
                if self.str in self.keywords: return Tok(self.loc, self.keywords[self.str])
                return Tok(self.loc, self.str)

            self.eat()
            err(self.loc.anew_begin(), f"invalid input char '{self.str}'")
