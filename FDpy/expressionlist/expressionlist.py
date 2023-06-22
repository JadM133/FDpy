from FDpy.treenode import postvisitor, evaluate
from FDpy.expressions import Symbol


class ExpressionList:
    def __init__(self, expr_list):
        self.expr_list = expr_list

    def __str__(self):
        return str(self.expr_list)

    def __repr__(self):
        return type(self).__name__ + repr(self.expr_list)

    def __add__(self, other):
        d1 = self.expr_list
        d2 = other.expr_list
        d_added = {k_val: d1.get(k_val, 0) + d2.get(k_val, 0) for k_val in (d1.keys() | d2.keys())}
        return ExpressionList(d_added)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            d1 = self.expr_list
            d_mul = {k: d1.get(k, 0) * other for k in (d1.keys())}
            return ExpressionList(d_mul)
        else:
            raise NotImplementedError

    def __sub__(self, other):
        d1 = self.expr_list
        d2 = other.expr_list
        d_sub = {k_val: d1.get(k_val, 0) - d2.get(k_val, 0) for k_val in (d1.keys() | d2.keys())}
        return ExpressionList(d_sub)

    def __truediv__(self, other):
        if isinstance(other, Symbol):
            d1 = self.expr_list
            d_div = {k: d1.get(k, 0) / other for k in (d1.keys())}
            return ExpressionList(d_div)
        else:
            raise NotImplementedError

    def __call__(self, val, symb):
        name = str(symb)
        expr = self.expr_list
        expr = ExpressionList({k: postvisitor(expr.get(k), evaluate, symbol_map={name: val}) for k in expr.keys()})
        expr.clean()
        return expr

    def __eq__(self, other):
        return self.expr_list == other.expr_list

    def inc(self, increment=1):
        return ExpressionList({k + increment: elem for k, elem in self.expr_list.items()})

    def dec(self, increment=1):
        return self.inc(-increment)

    def clean(self, val=0):
        self.expr_list = {k: v for k, v in self.expr_list.items() if v != val}

    def combine_x_and_t(self, other, time):
        t_dict = other.expr_list
        k_max = max(k for k in t_dict.keys())
        if time == "imp":
            t_max = ExpressionList({0: t_dict.get(k_max)})
            del t_dict[k_max]
            rhs_t = {k: -v for k, v in t_dict.items()}
            mat_dict = (t_max - self).expr_list
            rhs_x = None
            bc_x = self.expr_list
            del bc_x[0]
            return mat_dict, rhs_x, rhs_t, bc_x
        elif time == "exp":
            mat_dict = {0: t_dict.get(k_max)}
            del t_dict[k_max]
            rhs_t = {k: -v for k, v in t_dict.items()}
            rhs_x = self.expr_list
            del rhs_x[0]
            return mat_dict, rhs_x, rhs_t
        else:
            raise NotImplementedError
