"""Test functions in Fdproblem class."""


from FDpy.fd_problem import Fd_problem
import pytest
import numpy as np
from FDpy.expressions import Symbol


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
    """Test if errors are raised correctly."""
    with pytest.raises(ValueError):
        Fd_problem((0, 1), (0, 10), boundary, initial, equation, dx, dt)


x = Symbol('x')


@pytest.mark.parametrize(
    "initial, equation, act_res",
    [
        ((4, (0, 2), (0, 2, 1)), ((0, 0, 0, 1), (0, 0, 0, 0, 1)), [[4, 4, 4, 4], [8, 8, 8, 8], [16, 16, 16, 16]]),
        (4, ((0, 0, 0, 1), (0, 0, 1)), [[4, 4, 4, 4]]),
        ((4, 6), ((0, 0, 0, 1), (0, 0, 0, 1)), [[4, 4, 4, 4], [6, 6, 6, 6]]),
        ((4, (0, 1)), ((0, 0, 0, 1), (0, 0, 0, 1)), [[4, 4, 4, 4], [4, 4, 4, 4]]),
        ((np.ones(4), (0, 6)), ((0, 0, 0, 1), (0, 0, 0, 1)), [[1, 1, 1, 1], [6, 6, 6, 6]]),
        ((2*x-1, (0, 2)), ((0, 0, 0, 1), (0, 0, 0, 1)), [[-0.6, -0.2, 0.2, 0.6], [-1.2, -0.4, 0.4, 1.2]]),
    ],
)
def test_init_rhs(initial, equation, act_res):
    """Test if _init_rhs() is working properly."""
    P = Fd_problem((0, 1), (0, 1), (0, 0), initial, equation, dx=0.2, dt=0.2)
    res = np.around(P._init_rhs().tolist(), decimals=1)
    assert np.all(res == act_res), f"RHS is wrong, expected{act_res} but got {act_res}"


@pytest.mark.parametrize(
    "matrix, rhs, bc_x, first",
    [
        
    ],
)
def test_implement_bc(matrix, rhs, bc_x, first):
    """Test if boundary conditions are implemented properly."""
    
