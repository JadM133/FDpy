from fd_problem import Fd_problem
import pytest


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
