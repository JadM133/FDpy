import pytest
from FDpy.utils import _x_or_t_to_epxrlist
from FDpy.expressionlist import ExpressionList


@pytest.mark.parametrize(
    "equation, method, step_size, result",
    [
        ((1, 2, 1, 1), ["bac", "cen"], 0.1, {0: -188, 1: 100, -1: 90}),
    ],
)
def test_to_exprlist(equation, method, step_size, result):
    actual = _x_or_t_to_epxrlist(equation, method, step_size)
    assert ExpressionList(result) == actual, f"expected {result} but got {actual}"
