
"""Deifine tests for ExpressionList class."""


import pytest
from FDpy.expressionlist import ExpressionList
from FDpy.expressions import Symbol
from functools import singledispatch

x = Symbol("x")


@pytest.mark.parametrize(
    "d1, d2, sum_val",
    [
        ({0: 5, -1: 6, 1: 4}, {-2: 3, 0: 2, 1: -5}, {-2: 3, -1: 6, 0: 7, 1: -1}),
    ],
)
def test_add(d1, d2, sum_val):
    """Test addition between ExpressionLists."""
    d1 = ExpressionList(d1)
    d2 = ExpressionList(d2)
    sum_val = ExpressionList(sum_val)
    assert d1 + d2 == sum_val, f"expected {sum_val} but got {d1+d2}"


@pytest.mark.parametrize(
    "d1, d2, sub_val",
    [
        ({0: 5, -1: 6, 1: 4}, {-2: 3, 0: 2, 1: -5}, {-2: -3, -1: 6, 0: 3, 1: 9}),
    ],
)
def test_sub(d1, d2, sub_val):
    """Test substraction between ExpressionLists."""
    d1 = ExpressionList(d1)
    d2 = ExpressionList(d2)
    sub_val = ExpressionList(sub_val)
    assert d1 - d2 == sub_val, f"expected {sub_val} but got {d1-d2}"


@pytest.mark.parametrize(
    "d1, d2, div_val",
    [
        ({0: 5, -1: 6, 1: 4}, x, {0: 5 / x, -1: 6 / x, 1: 4 / x}),
        ({0: 5, -1: 6, 1: 4}, 2, None),
        ({0: 5, -1: 6, 1: 4}, {0: 3, 1: 4}, None),
    ],
)
def test_div(d1, d2, div_val):
    """Test substraction between ExpressionLists."""
    @singledispatch
    def testing(d1, d2, div_val):
        d1 = ExpressionList(d1)
        with pytest.raises(NotImplementedError):
            d1 / d2

    @testing.register(Symbol)
    def test_div(d1, d2, div_val):
        d1 = ExpressionList(d1)
        div_val = ExpressionList(div_val)
        assert d1 / d2 == div_val, f"expected {div_val} but got {d1/d2}"


@pytest.mark.parametrize(
    "d1, x_val, call_val",
    [
        ({0: 1 / x, -1: 5 * x, 1: x + 2}, 0.1, {0: 10, -1: 0.5, 1: 2.1}),
    ],
)
def test_call(d1, x_val, call_val):
    """Test evaluation of ExpressionLists."""
    d1 = ExpressionList(d1)
    val = d1(x_val, "x")
    call_val = ExpressionList(call_val)
    assert val == call_val, f"expected {call_val} but got {val}"


@pytest.mark.parametrize(
    "x_dict, t_dict, mat, rhs_x, rhs_t, bc_x",
    [
        ({0: 1, -1: 2, 1: 3}, {0: 4, 1: 5}, {-1: -2, 0: 4, 1: -3}, None, {0: -4}, {-1: 2, 1: 3}),
        ({0: -2, 1: 1, -1: 1}, {0: -2, 1: 2}, {0: 4, 1: -1, -1: -1}, None, {0: 2}, {1: 1, -1: 1})
    ],
)
def test_combine_x_and_t(x_dict, t_dict, mat, rhs_x, rhs_t, bc_x):
    """Test the method when implicit sschemes are used."""
    x = ExpressionList(x_dict)
    t = ExpressionList(t_dict)
    m, r1, r2, b = x.combine_x_and_t(t, "imp")
    assert m == mat, f"Wrong matrix, expected{mat} but got {m}"
    assert r1 == rhs_x, f"Wrong rhs (x), expected{rhs_x} but got {r1}"
    assert r2 == rhs_t, f"Wrong rhs (t), expected{rhs_t} but got {r2}"
    assert b == bc_x, f"Wrong bc (x), expected{bc_x} but got {b}"


x = ExpressionList({0: 1, -1: 2, 1: 3})
t = ExpressionList({0: 4, 1: 5})
a = x.combine_x_and_t(t, "imp")
