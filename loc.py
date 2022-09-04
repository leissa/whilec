class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self): return f'{self.row}:{self.col}'
    def __eq__(self, other): return self.row == other.row and self.col == other.col
    def __ne__(self, other): return self.row != other.row and self.col != other.col

class Loc:
    def __init__(self, file, begin, finis):
        self.file = file
        self.begin = begin
        self.finis = finis

    def __str__(self):
        if self.begin == self.finis:
            return f'{self.file}:{self.begin}'
        else:
            return f'{self.file}:{self.begin}-{self.finis}'