from copy import deepcopy
from enum import Enum, auto
import string

from err import err
from loc import *

class Tag(Enum):
    # delimiters
    D_brace_l   = auto()
    D_brace_r   = auto()
    D_paren_l   = auto()
    D_paren_r   = auto()
    # keywords
    K_true      = auto()
    K_false     = auto()
    K_while     = auto()
    # misc
    M_id        = auto()
    M_lit       = auto()
    M_eof       = auto()
    # further tokens
    T_add       = auto()
    T_sub       = auto()
    T_assign    = auto()
    T_semicolon = auto()

    def __str__(self):
        if self is self.D_brace_l:   return '{'
        if self is self.D_brace_r:   return '}'
        if self is self.D_paren_l:   return '('
        if self is self.D_paren_r:   return ')'
        if self is self.K_while:     return 'while'
        if self is self.M_id:        return '<identifier>'
        if self is self.M_lit:       return '<literal>'
        if self is self.M_eof:       return '<end of file>'
        if self is self.T_add:       return '+'
        if self is self.T_sub:       return '-'
        if self is self.T_assign:    return '='
        if self is self.T_semicolon: return ';'
        assert False

class Tok:
    def __init__(self, loc, arg):
        self.loc = deepcopy(loc)

        if isinstance(arg, str):
            self.tag = Tag.M_id
            self.id  = arg
        elif isinstance(arg, int):
            self.tag = Tag.M_lit
            self.lit = arg
        else:
            assert isinstance(arg, Tag)
            self.tag = arg

        print(f'{self.tag} -> {loc}')

    def isa(self, tag): return self.tag is tag

class Lexer:
    def __init__(self, filename):
        self.loc = Loc(filename, Pos(1, 1), Pos(1, 1))
        self.peek = Pos(1, 1)
        self.file = open(filename, "r")
        self.keywords = {
            "true":  Tag.K_true,
            "false": Tag.K_false,
            "while": Tag.K_while,
        }

    def accept_if(self, pred):
        tell = self.file.tell()
        char = self.file.read(1)

        if pred(char):
            self.str += char
            self.loc.finis = deepcopy(self.peek)

            if char == '': # end of file
                pass
            elif char == '\n':
                self.peek.row += 1
                self.peek.col = 1
            else:
                self.peek.col += 1
            return True;

        self.file.seek(tell) # undo read
        return False;

    def accept(self, char): return self.accept_if(lambda c : c == char)

    def lex(self):
        while True:
            self.loc.begin = deepcopy(self.peek)
            self.loc.finis = deepcopy(self.peek)
            self.str = ''

            if self.accept('' ): return Tok(self.loc, Tag.M_eof)
            if self.accept_if(lambda char : char in string.whitespace): continue
            if self.accept('{'): return Tok(self.loc, Tag.D_brace_l)
            if self.accept('}'): return Tok(self.loc, Tag.D_brace_r)
            if self.accept('('): return Tok(self.loc, Tag.D_paren_l)
            if self.accept(')'): return Tok(self.loc, Tag.D_paren_r)
            if self.accept('+'): return Tok(self.loc, Tag.T_add)
            if self.accept('-'): return Tok(self.loc, Tag.T_sub)
            if self.accept('='): return Tok(self.loc, Tag.T_assign)
            if self.accept(';'): return Tok(self.loc, Tag.T_semicolon)

            # literal
            if self.accept_if(lambda char : char in string.digits):
                while self.accept_if(lambda char : char in string.digits): pass
                return Tok(self.loc, int(self.str))

            # identifier
            if self.accept_if(lambda char : char in string.ascii_letters):
                while self.accept_if(lambda char : char in string.ascii_letters or char in string.digits): pass
                if self.str in self.keywords: return Tok(self.loc, self.keywords[self.str])
                return Tok(self.loc, self.str)

            self.accept_if(lambda _ : True) # eat unknown char
            err(self.loc.anew_begin(), f"illegal character '{self.str}' in input stream")
