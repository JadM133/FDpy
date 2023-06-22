import pytest
from expressionlist import ExpressionList
from expressions import Symbol
from functools import singledispatch

x = Symbol('x')


@pytest.mark.parametrize(
    "d1, d2, sum_val",
    [
        ({0: 5, -1: 6, 1: 4}, {-2: 3, 0: 2, 1: -5}, {-2: 3, -1: 6, 0: 7, 1: -1}),
    ],
)
def test_add(d1, d2, sum_val):
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
    d1 = ExpressionList(d1)
    d2 = ExpressionList(d2)
    sub_val = ExpressionList(sub_val)
    assert d1 - d2 == sub_val, f"expected {sub_val} but got {d1-d2}"


@pytest.mark.parametrize(
    "d1, d2, div_val",
    [
        ({0: 5, -1: 6, 1: 4}, x, {0: 5/x, -1: 6/x, 1: 4/x}),
        ({0: 5, -1: 6, 1: 4}, 2, None),
        ({0: 5, -1: 6, 1: 4}, {0: 3, 1: 4}, None),
    ],
)
def test_div(d1, d2, div_val):
    @singledispatch
    def testing(d1, d2, div_val):
        d1 = ExpressionList(d1)
        with pytest.raises(NotImplementedError):
            d1/d2

    @testing.register(Symbol)
    def test_div(d1, d2, div_val):
        d1 = ExpressionList(d1)
        div_val = ExpressionList(div_val)
        assert d1 / d2 == div_val, f"expected {div_val} but got {d1/d2}"


@pytest.mark.parametrize(
    "d1, x_val, call_val",
    [
        ({0: 1/x, -1: 5*x, 1: x+2}, 0.1, {0: 10, -1: 0.5, 1: 2.1}),
    ],
)
def test_call(d1, x_val, call_val):
    d1 = ExpressionList(d1)
    val = d1(x_val, x)
    call_val = ExpressionList(call_val)
    assert val == call_val, f"expected {call_val} but got {val}"


@pytest.mark.parametrize(
    "d1, res_val",
    [
        ({0: 1.1, -1: 5, 1: -2}, {1: 1.1, 0: 5, 2: -2}),
    ],
)
def test_inc(d1, res_val):
    d1 = ExpressionList(d1)
    res_val = ExpressionList(res_val)
    assert d1.inc() == res_val, f"expected {res_val} but got {d1.inc()}"


@pytest.mark.parametrize(
    "d1, res_val",
    [
        ({0: 1.1, -1: 5, 1: -2}, {-1: 1.1, -2: 5, 0: -2}),
    ],
)
def test_dec(d1, res_val):
    d1 = ExpressionList(d1)
    res_val = ExpressionList(res_val)
    assert d1.dec() == res_val, f"expected {res_val} but got {d1.dec()}"
