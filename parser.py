from lexer import Lexer

class Parser:
    def __init__(self, filename):
        self.lexer = Lexer(filename)
        self.ahead = self.lexer.lex()
