"""Test functions in Fdproblem class."""


import pytest
from FDpy.utils import _x_or_t_to_epxrlist
from FDpy.expressionlist import ExpressionList
import numpy as np


@pytest.mark.parametrize(
    "eq, methodt, acc, dic, str_val",
    [
        (
            (0, 2, 1, 3),
            "cen",
            2,
            {
                0: -600 + 2,
                1: 300 + 5,
                -1: 300 - 5,
            },
            "2.0*U(i,j)+(0.5*U(i,j+1)-0.5*U(i,j-1))/dt^1+(-6.0*U(i,j)+3.0*U(i,j+1)+3.0*U(i,j-1))/dt^2",
        ),
        (
            (0, 0, 0, 0, 0, 1),
            "cen",
            4,
            {
                0: np.round(28 / 3 * 10000),
                1: -13 / 2 * 10000,
                -1: -13 / 2 * 10000,
                2: 2 * 10000,
                -2: 2 * 10000,
                3: np.round(-1 / 6 * 10000),
                -3: np.round(-1 / 6 * 10000),
            },
            "(9.33*U(i,j)-6.5*U(i,j+1)-6.5*U(i,j-1)+2.0*U(i,j+2)+2.0*U(i,j-2)-0.17*U(i,j+3)-0.17*U(i,j-3))/dt^4",
        ),
        (
            (0, 0, 0, 1),
            "for",
            3,
            {
                0: np.round(35 / 12 * 100),
                1: np.round(-26 / 3 * 100),
                2: 19 / 2 * 100,
                3: np.round(-14 / 3 * 100),
                4: np.round(11 / 12 * 100),
            },
            "(2.92*U(i,j)-8.67*U(i,j+1)+9.5*U(i,j+2)-4.67*U(i,j+3)+0.92*U(i,j+4))/dt^2",
        ),
    ],
)
def test_t_x_or_t_to_epxrlist(eq, methodt, acc, dic, str_val):
    """Test the function that generates Expression and ExpressionList from the (t) part of the equation."""
    act_result = _x_or_t_to_epxrlist(eq, methodt, "dt", 0.1, acc=acc)
    act_expr, act_coef, _ = act_result
    act_coef = act_coef.round_vals()
    true_coef = ExpressionList(dic)
    assert (str(act_expr) == str_val) and (true_coef == act_coef), f"expected {str_val} but got {str(act_expr)}"


eq, methodt, acc = (0, 0, 0, 1), "for", 3
expr, _, _ = _x_or_t_to_epxrlist(eq, methodt, "dt", 0.1, acc=acc)
print(expr)


@pytest.mark.parametrize(
    "eq, methodx, acc, order_t, dic, str_val",
    [
        (
            (0, 2, 1, 3),
            "cen",
            2,
            1,
            {
                0: -600 + 2,
                1: 300 + 5,
                -1: 300 - 5,
            },
            "2.0*U(i,j+1)+(0.5*U(i+1,j+1)-0.5*U(i-1,j+1))/dx^1+(-6.0*U(i,j+1)+3.0*U(i+1,j+1)+3.0*U(i-1,j+1))/dx^2",
        ),
        (
            (0, 0, 0, 0, 0, 1),
            "cen",
            4,
            2,
            {
                0: np.round(28 / 3 * 10000),
                1: -13 / 2 * 10000,
                -1: -13 / 2 * 10000,
                2: 2 * 10000,
                -2: 2 * 10000,
                3: np.round(-1 / 6 * 10000),
                -3: np.round(-1 / 6 * 10000),
            },
            "(9.33*U(i,j+2)-6.5*U(i+1,j+2)-6.5*U(i-1,j+2)+2.0*U(i+2,j+2)+2.0*U(i-2,j+2)-0.17*U(i+3,j+2)-0.17*U(i-3,j+2))/dx^4",
        ),
        (
            (0, 0, 0, 1),
            "for",
            3,
            0,
            {
                0: np.round(35 / 12 * 100),
                1: np.round(-26 / 3 * 100),
                2: 19 / 2 * 100,
                3: np.round(-14 / 3 * 100),
                4: np.round(11 / 12 * 100),
            },
            "(2.92*U(i,j)-8.67*U(i+1,j)+9.5*U(i+2,j)-4.67*U(i+3,j)+0.92*U(i+4,j))/dx^2",
        ),
    ],
)
def test_x_x_or_t_to_epxrlist(eq, methodx, acc, order_t, dic, str_val):
    """Test the function that generates Expression and ExpressionList from the (x) part of the equation."""
    act_result = _x_or_t_to_epxrlist(eq, methodx, "dx", 0.1, acc=acc, order_t=order_t)
    act_expr, act_coef, _ = act_result
    act_coef = act_coef.round_vals()
    true_coef = ExpressionList(dic)
    assert (str(act_expr) == str_val) and (true_coef == act_coef), f"expected {str_val} but got {str(act_expr)}"
