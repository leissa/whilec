import string
from enum import Enum, auto
from pos import *

class Tok:
    class Tag(Enum):
        # keywords
        K_while     = auto(),
        # misc
        M_id        = auto(),
        M_lit       = auto(),
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
            if self is Tok.Tag.M_lit:
                return '<literal>'
            if self is Tok.Tag.T_add:
                return '+'
            if self is Tok.Tag.T_sub:
                return '-'
            if self is Tok.Tag.T_assign:
                return '='
            if self is Tok.Tag.T_semicolon:
                return ';'
            assert False

    def __init__(self, loc, arg):
        self.loc = loc

        if isinstance(arg, str):
            self.tag = Tok.Tag.M_id
            self.sym = arg
        elif isinstance(arg, int):
            self.tag = Tok.Tag.M_lit
            self.val = arg
        else:
            assert isinstance(arg, Tok.Tag)
            self.tag = arg

        print(self.tag)

class Lexer:
    def __init__(self, filename):
        self.file = open(filename, "r")
        self.keywords = {
            "while": Tok.Tag.K_while
            # other keywords go here
        }

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

            if self.accept_if(lambda char : char in string.digits):
                while self.accept_if(lambda char : char in string.digits):
                    pass
                return Tok(self.pos, int(self.str))

            if self.accept_if(lambda char : char in string.ascii_letters):
                while self.accept_if(lambda char : char in string.ascii_letters or char in string.digits):
                    pass
                if self.str in self.keywords:
                    return Tok(self.pos, Tok.Tag.self.keywords[self.str])
                return Tok(self.pos, self.str)

            print('error')
            break
