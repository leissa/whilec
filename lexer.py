"""
Lexes an input file and produces Tokens.
"""

from copy import deepcopy
import string

from err import err
from loc import Pos, Loc
from tok import Tag, Tok

class Lexer:
    def __init__(self, file):
        self.file = file
        self.loc  = Loc(file.name, Pos(1, 1), Pos(1, 1))
        self.peek = Pos(1, 1)
        self.str  = ""
        self.keywords = {
            "and"   : Tag.K_AND,
            "or"    : Tag.K_OR,
            "not"   : Tag.K_NOT,
            "bool"  : Tag.K_BOOL,
            "int"   : Tag.K_INT,
            "true"  : Tag.K_TRUE,
            "false" : Tag.K_FALSE,
            "return": Tag.K_RETURN,
            "while" : Tag.K_WHILE,
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
            return True

        self.file.seek(tell) # undo read
        return False

    def eat(self):
        self.accept_if(lambda _ : True)

    def accept(self, char):
        return self.accept_if(lambda c : c == char)

    def lex(self):
        while True:
            self.loc.begin = deepcopy(self.peek)
            self.loc.finis = deepcopy(self.peek)
            self.str = ""

            if self.accept("" ): return Tok(self.loc, Tag.M_EOF)
            if self.accept_if(lambda char : char in string.whitespace):
                continue
            if self.accept("{"): return Tok(self.loc, Tag.D_BRACE_L)
            if self.accept("}"): return Tok(self.loc, Tag.D_BRACE_R)
            if self.accept("("): return Tok(self.loc, Tag.D_PAREN_L)
            if self.accept(")"): return Tok(self.loc, Tag.D_PAREN_R)
            if self.accept("+"): return Tok(self.loc, Tag.T_ADD)
            if self.accept("-"): return Tok(self.loc, Tag.T_SUB)
            if self.accept("*"): return Tok(self.loc, Tag.T_MUL)
            if self.accept(";"): return Tok(self.loc, Tag.T_SEMICOLON)

            if self.accept("="):
                if self.accept("="): return Tok(self.loc, Tag.T_EQ)
                return Tok(self.loc, Tag.T_ASSIGN)

            if self.accept("<"):
                if self.accept("="): return Tok(self.loc, Tag.T_LE)
                return Tok(self.loc, Tag.T_LT)

            if self.accept(">"):
                if self.accept("="): return Tok(self.loc, Tag.T_GE)
                return Tok(self.loc, Tag.T_GT)

            if self.accept("!"):
                if self.accept("="): return Tok(self.loc, Tag.T_NE)
                self.eat()
                err(self.loc.anew_begin(), f"invalid input char '{self.str}'; maybe you wanted to use '!='?")
                continue

            # literal
            if self.accept_if(lambda char : char in string.digits):
                while self.accept_if(lambda char : char in string.digits):
                    pass
                return Tok(self.loc, int(self.str))

            # identifier
            if self.accept_if(lambda char : char in string.ascii_letters):
                while self.accept_if(lambda char : char in string.ascii_letters or char in string.digits):
                    pass
                if self.str in self.keywords: return Tok(self.loc, self.keywords[self.str])
                return Tok(self.loc, self.str)

            self.eat()
            err(self.loc.anew_begin(), f"invalid input char '{self.str}'")
