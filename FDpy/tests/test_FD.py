"""Test functions in Fdproblem class."""


from FDpy.fd_problem import Fd_problem
import pytest


@pytest.mark.parametrize(
    "boundary, initial, equation, str_val",
    [
        ((0, 0, 1, 2, 4), 5, ((1, -1, 0, 4, 5, 0, 10), (2, 0, -1)), "Equation: +10Uxxxxx +5Uxxx +4Uxx -1U -1 = -1Ut"),
        ([(0, 1)], 0, ((2, 3, 10), (2, 3, 1)), "Equation: +10Ux = +1Ut"),
        ((0, 0, 1, 2), None, ((5, 0, 0, 0, 0, 1), (2, 3)), "Equation: +1Uxxxx -3U +3 = 0"),
    ],
)
def test_str(boundary, initial, equation, str_val):
    """Test how Fdproblem instances are printed."""
    pred = str(Fd_problem((0, 10), (0, 1), boundary=boundary, initial=initial, equation=equation))
    assert pred == str_val, f"Incorrect return value from __str__, expected {str_val} got {pred}"


@pytest.mark.parametrize(
    "boundary, initial, equation, dx, dt",
    [
        ((0, 0, 1, 2, 3), 5, ((1, -1, 0, 4, 5, 2, 0), (2, 0, -1)), 0.1, 0.1),
        (2, 0, ((2, 3, 10), (2, 3, 1, 0)), -0.1, 0.2),
        (2, 0, ((2, 3, 10, 5), (2, 3, 1)), 0.1, 0.1),
        (2, 0, ((2, 3, 10), (2, 3, 1)), 0, 0.1),
        (2, 0, ((2, 3, 10), (2, 3, 1)), 0.1, 0),
        (2, 0, ((2, 3, 10), (2, 3, 1)), 0.1, -0.2),
        (2, 0, ((2, 3, 10), (2, 3, 1)), -0.1, 0.2),
        (2, 0, ((2, 3, 10), (2, 3, 1, 2)), -0.1, 0.2),
    ],
)
def test_raise_errors(boundary, initial, equation, dx, dt):
    """Test how Fdproblem instances are printed."""
    with pytest.raises(ValueError):
        Fd_problem((0, 1), (0, 10), boundary, initial, equation, dx, dt)
