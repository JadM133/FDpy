from fd_problem import Fd_problem
import pytest
from utils import _equ_to_exprlist
from expressionlist import ExpressionList


@pytest.mark.parametrize(
    "domain, interval, boundary, initial, method, equation, str_val",
    [
        (
            (0, 1),
            (0, 10),
            (0, 0),
            (1),
            "Imp",
            ((1, -1, 0, 4, 5, 0, 10), (2, 0, 1)),
            "Equation: +10Uxxxxx +5Uxxx +4Uxx -1U -1 = +1Ut, \n"
            + "BC: U = 0 at x = 0, U = 0 at x = 1, \nIC: U = 1 at t = 0,"
            + " \nMethod: Implicit Finite Differences.",
        ),
        (
            (0, 6),
            (0, 10),
            (0, 2),
            (0),
            "Imp",
            ((2, 3, 10), (2, 3, 1)),
            "Equation: +10Ux = +1Ut, \n"
            + "BC: U = 0 at x = 0, U = 2 at x = 6, \nIC: U = 0 at t = 0,"
            + " \nMethod: Implicit Finite Differences.",
        ),
        (
            (0, 4),
            (2, 9),
            (0, 10),
            (4),
            "Imp",
            ((5, 0, 0, 0, 0, 1), (2, 3)),
            "Equation: +1Uxxxx -3U +3 = 0, \n"
            + "BC: U = 0 at x = 0, U = 10 at x = 4, \nIC: U = 4 at t = 2,"
            + " \nMethod: Implicit Finite Differences.",
        ),
    ],
)
def test_str(domain, interval, boundary, initial, method, equation, str_val):
    assert (
        str(Fd_problem(domain, interval, boundary, initial, method, equation))
        == str_val
    ), "Incorrect return value from __str__"


@pytest.mark.parametrize(
    "eq, method1, methodn, dx, dt, resultx, resultt",
    [
        (
            ((0, 1, 1, 0, 0, 1), (0, 0, 2, 3)),
            ("for", "cen"),
            ("for", "cen"),
            0.1,
            0.1,
            {
                0: -20000 + 1 - 10,
                1: 30000 + 10,
                -1: 30000,
                2: -30000,
                -2: -30000,
                3: 10000,
                -3: 10000,
            },
            {
                -1: 300,
                0: -20 - 600,
                1: 20 + 300,
            },
        ),
        (
            ((0, 0, 0, 1), (0, 0, 0, 2)),
            ("for", "cen"),
            ("for", "cen"),
            0.1,
            0.1,
            {0: -200, -1: 100, 1: 100},
            {0: -400, -1: 200, 1: 200},
        ),
        (
            ((0, 0, 0, 1), (0, 0, 0, 1)),
            ("for", "bac"),
            ("for", "for"),
            0.1,
            0.1,
            {0: 100, -1: -200, -2: 100},
            {0: 100, 1: -200, 2: 100},
        ),
        (
            ((0, 1, 0, 0), (0, 0, 1)),
            ("for", "cen"),
            ("cen", "cen"),
            0.1,
            0.1,
            {0: 1},
            {1: 5, -1: -5},
        ),
        (
            ((0, 0, 1, 0), (0, 0, 1)),
            ("for", "cen"),
            ("bac", "cen"),
            0.1,
            0.1,
            {0: -10, 1: 10},
            {-1: -10, 0: 10},
        ),
        (
            ((0, 0, 0, 0, 0, 1), (0, 0, 1)),
            ("for", "cen"),
            ("for", "cen"),
            0.1,
            0.2,
            {
                0: -20000,
                1: 30000,
                -1: 30000,
                2: -30000,
                -2: -30000,
                3: 10000,
                -3: 10000,
            },
            {0: -5, 1: 5},
        ),
    ],
)
def test_equ_to_exprlist(eq, method1, methodn, dx, dt, resultx, resultt):
    act_result = _equ_to_exprlist(eq, method1, methodn, dx, dt)
    act_x, act_t = act_result
    true_x = ExpressionList(resultx)
    true_t = ExpressionList(resultt)
    assert (act_x == true_x) and (
        act_t == true_t
    ), f"expected {true_x, true_t} but got {act_result}"
