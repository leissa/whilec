"""
These are all tokens While knows.
"""

from enum import Enum, auto

class Tag(Enum):
    # delimiters
    D_BRACE_L   = auto()
    D_BRACE_R   = auto()
    D_PAREN_L   = auto()
    D_PAREN_R   = auto()
    # keywords
    K_BOOL      = auto()
    K_INT       = auto()
    K_AND       = auto()
    K_OR        = auto()
    K_NOT       = auto()
    K_TRUE      = auto()
    K_FALSE     = auto()
    K_RETURN    = auto()
    K_IF        = auto()
    K_ELSE      = auto()
    K_WHILE     = auto()
    # misc
    M_SYM       = auto()
    M_LIT       = auto()
    M_EOF       = auto()
    # further Tokens
    T_ADD       = auto()
    T_SUB       = auto()
    T_MUL       = auto()
    T_EQ        = auto()
    T_NE        = auto()
    T_LT        = auto()
    T_LE        = auto()
    T_GT        = auto()
    T_GE        = auto()
    T_ASSIGN    = auto()
    T_SEMICOLON = auto()

    def __str__(self):
        if self is self.D_BRACE_L:   return "{"
        if self is self.D_BRACE_R:   return "}"
        if self is self.D_PAREN_L:   return "("
        if self is self.D_PAREN_R:   return ")"
        if self is self.K_BOOL:      return "bool"
        if self is self.K_INT:       return "int"
        if self is self.K_AND:       return "and"
        if self is self.K_OR:        return "or"
        if self is self.K_NOT:       return "not"
        if self is self.K_TRUE:      return "true"
        if self is self.K_FALSE:     return "false"
        if self is self.K_RETURN:    return "return"
        if self is self.K_WHILE:     return "while"
        if self is self.M_SYM:       return "<identifier>"
        if self is self.M_LIT:       return "<literal>"
        if self is self.M_EOF:       return "<end of file>"
        if self is self.T_ADD:       return "+"
        if self is self.T_SUB:       return "-"
        if self is self.T_MUL:       return "*"
        if self is self.T_EQ:        return "=="
        if self is self.T_NE:        return "!="
        if self is self.T_LT:        return "<"
        if self is self.T_LE:        return "<="
        if self is self.T_GT:        return ">"
        if self is self.T_GE:        return ">="
        if self is self.T_ASSIGN:    return "="
        if self is self.T_SEMICOLON: return ";"
        assert False

    def is_type(self):
        return self is Tag.K_BOOL or self is Tag.K_INT

    def is_bin_op(self):
        return self is self.T_ADD \
            or self is self.T_SUB \
            or self is self.T_MUL \
            or self is self.T_EQ  \
            or self is self.T_NE  \
            or self is self.T_LT  \
            or self is self.T_LE  \
            or self is self.T_GT  \
            or self is self.T_GE  \
            or self is self.K_AND \
            or self is self.K_OR

    def is_arith(self):
        return self is self.T_ADD \
            or self is self.T_SUB \
            or self is self.T_MUL

    def is_rel(self):
        return self is self.T_EQ \
            or self is self.T_NE \
            or self is self.T_LT \
            or self is self.T_LE \
            or self is self.T_GT \
            or self is self.T_GE

    def is_logic(self): # binary only - K_not is its own thing
        return self is self.K_AND \
            or self is self.K_OR

    def is_unary(self):
        return self is self.T_ADD \
            or self is self.T_SUB \
            or self is self.K_NOT

class Tok:
    def __init__(self, loc, arg):
        self.loc = loc.copy()

        if isinstance(arg, str):
            self.tag = Tag.M_SYM
            self.sym = arg
        elif isinstance(arg, int):
            self.tag = Tag.M_LIT
            self.val = arg
        else:
            assert isinstance(arg, Tag)
            self.tag = arg

    def __str__(self):
        if self.isa(Tag.M_SYM): return self.sym
        if self.isa(Tag.M_LIT): return str(self.val)
        return self.tag.__str__()

    def isa(self, tag):
        return self.tag is tag

    def is_type(self):
        return self.tag.is_type()

    def is_bin_op(self):
        return self.tag.is_bin_op()

    def is_error(self):
        return self.sym == "<error>"
