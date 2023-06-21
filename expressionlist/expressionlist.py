from treenode import postvisitor, evaluate
from expressions import Symbol


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
        d_added = {k: d1.get(k, 0) + d2.get(k, 0) for k in (d1.keys() | d2.keys())}
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
        d_sub = {k: d1.get(k, 0) - d2.get(k, 0) for k in (d1.keys() | d2.keys())}
        return ExpressionList(d_sub)

    def __truediv__(self, other):
        if isinstance(other, Symbol):
            d1 = self.expr_list
            d_div = {k: d1.get(k, 0) / other for k in (d1.keys())}
            return ExpressionList(d_div)
        else:
            raise NotImplementedError

    def __call__(self, dx):
        expr = self.expr_list
        expr = {
            k: postvisitor(expr.get(k), evaluate, symbol_map={"dx": dx})
            for k in expr.keys()
        }
        return expr

    def inc(self, increment=1):
        return ExpressionList(
            {k + increment: elem for k, elem in self.expr_list.items()}
        )

    def dec(self, increment=1):
        return self.inc(-increment)
