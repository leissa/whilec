from enum import Enum, auto

class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col

class Loc:
    def __init__(self, file, begin, finis):
        self.file = file
        self.begin = begin
        self.finis = finis

class Tok:
    class Tag:
        # keywords
        K_while     = auto(),
        # misc
        M_while     = auto(),
        M_eof       = auto(),
        # further tokens
        T_add       = auto(),
        T_sub       = auto(),
        T_assign    = auto(),
        T_semicolon = auto(),

    def __init__(self, tag):
        self.tag = tag
