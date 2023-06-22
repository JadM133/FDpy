from expressions import expressions, Expressions, Number
from functools import singledispatch


class TreeNode:
    def __init__(self, value, *children):
        self.value = value
        self.children = children

    def __repr__(self):
        return f"{type(self).__name__}{(self.value,) + self.children}"

    def __str__(self):
        childstring = ", ".join(map(str, self.children))
        return f"{self.value!s} -> ({childstring})"


def postvisitor(expr, fn, **kwargs):
    if not isinstance(expr, Expressions):
        expr = Number(expr)
    return fn(expr, *(postvisitor(c, fn, **kwargs) for c in expr.operands), **kwargs)


@singledispatch
def evaluate(expr, *o, **kwargs):
    raise NotImplementedError(f"Cannot evaluate a {type(expr).__name__}")


@evaluate.register(expressions.Number)
def _(expr, *o, **kwargs):
    return expr.value


@evaluate.register(expressions.Symbol)
def _(expr, *o, symbol_map, **kwargs):
    return symbol_map[expr.value]


@evaluate.register(expressions.Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@evaluate.register(expressions.Sub)
def _(expr, *o, **kwargs):
    return o[0] - o[1]


@evaluate.register(expressions.Mul)
def _(expr, *o, **kwargs):
    return o[0] * o[1]


@evaluate.register(expressions.Div)
def _(expr, *o, **kwargs):
    return o[0] / o[1]


@evaluate.register(expressions.Pow)
def _(expr, *o, **kwargs):
    return o[0] ** o[1]


@evaluate.register(expressions.F)
def _(expr, *o, **kwargs):
    fac = 1
    for num in range(o[0]):
        fac *= num + 1
    return fac
