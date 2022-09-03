import string
from enum import Enum, auto
from pos import *

class Tok:
    class Tag(Enum):
        # keywords
        K_while     = auto(),
        # misc
        M_id        = auto(),
        M_eof       = auto(),
        # further tokens
        T_add       = auto(),
        T_sub       = auto(),
        T_assign    = auto(),
        T_semicolon = auto(),

        def __str__(self):
            if self is Tok.Tag.K_while:
                return 'while'
            if self is Tok.Tag.M_id:
                return '<identifier>'
            if self is Tok.Tag.T_add:
                return '+'
            if self is Tok.Tag.T_sub:
                return '-'
            if self is Tok.Tag.T_assign:
                return '='
            if self is Tok.Tag.T_semicolon:
                return ';'
            assert False

    def __init__(self, loc, tag):
        self.loc = loc
        self.tag = tag
        print(f'tag: {self.tag}')

class Lexer:
    def __init__(self, filename):
        self.file = open(filename, "r")

    def accept_if(self, pred):
        tell = self.file.tell()
        char = self.file.read(1)

        if pred(char):
            self.str += char
            return True;

        self.file.seek(tell) # undo read
        return False;

    def accept(self, char):
        return self.accept_if(lambda c : c == char)

    def lex(self):
        self.pos = Pos(1, 1)

        while True:
            self.str = ''

            if self.accept_if(lambda char : char in string.whitespace):
                continue
            if self.accept('+'):
                return Tok(self.pos, Tok.Tag.T_add)
            if self.accept('-'):
                return Tok(self.pos, Tok.Tag.T_sub)
            if self.accept('='):
                return Tok(self.pos, Tok.Tag.T_assign)
            if self.accept(';'):
                return Tok(self.pos, Tok.Tag.T_semicolon)

            print('error')
            break
