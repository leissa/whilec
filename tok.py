from enum import Enum, auto
from loc import *

class Tag(Enum):
    # delimiters
    D_brace_l   = auto()
    D_brace_r   = auto()
    D_paren_l   = auto()
    D_paren_r   = auto()
    # keywords
    K_bool      = auto()
    K_int       = auto()
    K_and       = auto()
    K_or        = auto()
    K_not       = auto()
    K_true      = auto()
    K_false     = auto()
    K_return    = auto()
    K_while     = auto()
    # misc
    M_id        = auto()
    M_lit       = auto()
    M_eof       = auto()
    # further tokens
    T_add       = auto()
    T_sub       = auto()
    T_mul       = auto()
    T_eq        = auto()
    T_ne        = auto()
    T_lt        = auto()
    T_le        = auto()
    T_gt        = auto()
    T_ge        = auto()
    T_assign    = auto()
    T_semicolon = auto()

    def __str__(self):
        if self is self.D_brace_l:   return "{"
        if self is self.D_brace_r:   return "}"
        if self is self.D_paren_l:   return "("
        if self is self.D_paren_r:   return ")"
        if self is self.K_bool:      return "bool"
        if self is self.K_int:       return "int"
        if self is self.K_and:       return "and"
        if self is self.K_or:        return "or"
        if self is self.K_not:       return "not"
        if self is self.K_true:      return "true"
        if self is self.K_false:     return "false"
        if self is self.K_return:    return "return"
        if self is self.K_while:     return "while"
        if self is self.M_id:        return "<identifier>"
        if self is self.M_lit:       return "<literal>"
        if self is self.M_eof:       return "<end of file>"
        if self is self.T_add:       return "+"
        if self is self.T_sub:       return "-"
        if self is self.T_mul:       return "*"
        if self is self.T_eq:        return "=="
        if self is self.T_ne:        return "!="
        if self is self.T_lt:        return "<"
        if self is self.T_le:        return "<="
        if self is self.T_gt:        return ">"
        if self is self.T_ge:        return ">="
        if self is self.T_assign:    return "="
        if self is self.T_semicolon: return ";"
        assert False

    def is_type(self): return self is Tag.K_bool or self is Tag.K_int

    def is_bin_op(self):
        return self is self.T_add \
            or self is self.T_sub \
            or self is self.T_mul \
            or self is self.T_eq  \
            or self is self.T_ne  \
            or self is self.T_lt  \
            or self is self.T_le  \
            or self is self.T_gt  \
            or self is self.T_ge  \
            or self is self.K_and \
            or self is self.K_or

    def is_arith(self):
        return self is self.T_add \
            or self is self.T_sub \
            or self is self.T_mul

    def is_rel(self):
        return self is self.T_eq \
            or self is self.T_ne \
            or self is self.T_lt \
            or self is self.T_le \
            or self is self.T_gt \
            or self is self.T_ge

    def is_logic(self): # binary only - K_not is its own thing
        return self is self.K_and \
            or self is self.K_or

    def is_unary(self):
        return self is self.T_add \
            or self is self.T_sub \
            or self is self.K_not

class Tok:
    def __init__(self, loc, arg):
        self.loc = loc.copy()

        if isinstance(arg, str):
            self.tag = Tag.M_id
            self.id  = arg
        elif isinstance(arg, int):
            self.tag = Tag.M_lit
            self.val = arg
        else:
            assert isinstance(arg, Tag)
            self.tag = arg

    def __str__(self):
        if self.isa(Tag.M_id):  return self.id
        if self.isa(Tag.M_lit): return str(self.val)
        return self.tag.__str__()

    def isa(self, tag): return self.tag is tag
    def is_type(self): return self.tag.is_type()
    def is_bin_op(self): return self.tag.is_bin_op()
    def is_error(self): return self.id == "<error>"
