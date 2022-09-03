from tok import *

class Lexer:
    def __init__(self, filename):
        self.file = open(filename, "r")

    def accept(self, item):
        tell = self.file.tell()
        data = self.file.read(len(item))

        if data == item:
            self.str_ += data
            return True;

        self.file.seek(tell)
        return False;

    def lex(self):
        self.str_ = ''
        self.pos_ = Pos(1, 1)

        while True:
            if self.accept("+"):
                return Tok(Tok.Tag.T_add, pos_)
            if self.accept("-"):
                return Tok(Tok.Tag.T_sub, pos_)
            break
