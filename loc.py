"""
Helpers to keep track of source code locations.
"""

from copy import deepcopy

class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self): return f"{self.row}:{self.col}"
    def __eq__(self, other): return self.row == other.row and self.col == other.col
    def __ne__(self, other): return not (self == other)

class Loc:
    def __init__(self, file, begin, finis):
        self.file = file
        self.begin = begin
        self.finis = finis

    def __str__(self):
        if self.begin == self.finis:
            return f"{self.file}:{self.begin}"
        elif self.begin.row == self.finis.row:
            return f"{self.file}:{self.begin}-{self.finis.col}"
        else:
            return f"{self.file}:{self.begin}-{self.finis}"

    def anew_begin(self): return Loc(self.file, self.begin, self.begin)
    def anew_finis(self): return Loc(self.file, self.finis, self.finis)
    def copy(self): return Loc(self.file, deepcopy(self.begin), deepcopy(self.finis))
