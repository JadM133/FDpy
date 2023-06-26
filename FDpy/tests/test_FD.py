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
    pred = str(Fd_problem((0, 10), (0, 1), equation=equation, boundary=boundary, initial=initial))
    assert pred == str_val, f"Incorrect return value from __str__, expected {str_val} got {pred}"


x = Symbol("x")


@pytest.mark.parametrize(
    "initial, equation, act_res",
    [
        ((4, (0, 2), (0, 2, 1)), ((0, 0, 0, 1), (0, 0, 0, 0, 1)), [[4, 4, 4, 4], [8, 8, 8, 8], [16, 16, 16, 16]]),
        (4, ((0, 0, 0, 1), (0, 0, 1)), [[4, 4, 4, 4]]),
        ((4, 6), ((0, 0, 0, 1), (0, 0, 0, 1)), [[4, 4, 4, 4], [6, 6, 6, 6]]),
        ((4, (0, 1)), ((0, 0, 0, 1), (0, 0, 0, 1)), [[4, 4, 4, 4], [4, 4, 4, 4]]),
        ((np.ones(4), (0, 6)), ((0, 0, 0, 1), (0, 0, 0, 1)), [[1, 1, 1, 1], [6, 6, 6, 6]]),
        ((2 * x - 1, (0, 2)), ((0, 0, 0, 1), (0, 0, 0, 1)), [[-0.6, -0.2, 0.2, 0.6], [-1.2, -0.4, 0.4, 1.2]]),
    ],
)
def test_init_rhs(initial, equation, act_res):
    """Test if _init_rhs() is working properly."""
    P = Fd_problem((0, 1), (0, 1), equation, (0, 0), initial, dx=0.2, dt=0.2)
    res = np.around(P._init_rhs().tolist(), decimals=1)
    assert np.all(res == act_res), f"RHS is wrong, expected{act_res} but got {act_res}"


@pytest.mark.parametrize(
    "bo, equation, bc_x, bc_map, size, exp_rhs",
    [
        (1, ((0, 0, 1), (0, 0, 1)), np.array([[1], [5]]), [-1], 4, [0, 0, 0, 5]),
        (1, ((0, 0, 1), (0, 0, 1)), np.array([[-1], [-5]]), [0], 4, [-5, 0, 0, 0]),
        ([(1, 1, 2, 3)], ((0, 0, 1), (0, 0, 1)), np.array([[-1], [-5]]), [0], 4, [-5, 0, 0, 0]),
        ((1, 1), ((0, 0, 0, 1), (0, 0, 1)), np.array([[-1, 1], [25, 25]]), [0, -1], 4, [25, 0, 0, 25]),
        (
            [1, 1, 2],
            ((0, 0, 0, 0, 1), (0, 0, 1)),
            np.array([[-1, 1, 2], [-375, -125, 125]]),
            [0, -1, -2],
            4,
            [-375, 0, 250, -125],
        ),
        (
            [(1, 50), 4, 6, -2, 3, 1],
            ((0, 0, 0, 0, 1), (0, 0, 1)),
            np.array([[-3, -2, -1, 1, 2, 3], [-203.13, -125, -15.63, 15.63, 125, 203.13]]),
            [2, 1, 0, -1, -3, -2],
            6,
            [-15.63 - 500 - 1218.78, -125 - 812.52, -203.13, 609.39, 375 + 203.13, 46.89 + 125 - 406.26],
        ),
    ],
)
def test_implement_bc_rhs(bo, equation, bc_x, bc_map, size, exp_rhs):
    """Test if boundary conditions are implemented properly in the rhs.

    Note: the values of bc_x corresponding to the functions were computed
    manually using previously tested functions.

    Note: bc_x was computed using previousl tested methods.
    """
    P = Fd_problem((0, 1), (0, 1), equation, bo, (1), dx=0.2, dt=0.2, bc_map=bc_map)
    act_rhs, _ = P._implement_bc(np.zeros((size, size)), np.zeros(size), bc_x, False)
    act_rhs = np.around(act_rhs, decimals=2)
    exp_rhs = np.around(exp_rhs, decimals=2)
    assert np.all(act_rhs.tolist() == exp_rhs), f"RHS is wrong. Expected {exp_rhs} but got {act_rhs}."


@pytest.mark.parametrize(
    "bo, equation, bc_x, bc_map, size, exp_mat, check_type",
    [
        (1, ((0, 0, 1), (0, 0, 1)), np.array([[1], [5]]), [-1], 4, np.zeros(4), 1),
        ([(0, 1, 2)], ((0, 0, 1), (0, 0, 1)), np.array([[-1], [-5]]), [0], 4, [(0, 0, 5), (0, 1, 10)], 0),
        (
            [(0, 1, 2), (0, 2, 3), (0, 4, 5)],
            ((0, 0, 0, 0, 1), (0, 0, 1)),
            np.array([[-1, 1, 2], [-375, -125, 125]]),
            [0, -1, -2],
            4,
            [(0, 0, 375), (0, 1, 2 * 375), (2, 3, -500), (2, 2, -625), (3, 3, 500 - 250), (3, 2, 625 - 375)],
            0,
        ),
        (
            [(1, 5), (4, 3, 2), (6, 1), -2, 3, 1],
            ((0, 0, 0, 0, 1), (0, 0, 1)),
            np.array([[-3, -2, -1, 1, 2, 3], [-203.13, -125, -15.63, 15.63, 125, 203.13]]),
            [2, 1, 0, -1, -3, -2],
            6,
            [(2, 0, 1015.65), (1, 0, 625 + 609.38), (1, 1, 406.26), (0, 0, 78.15 + 375 + 203.13), (0, 1, 250)],
            0,
        ),
    ],
)
def test_implement_bc_mat(bo, equation, bc_x, bc_map, size, exp_mat, check_type):
    """Test if boundary conditions are implemented properly in the rhs.

    Note: the values of bc_x corresponding to the functions were computed
    manually using previously tested functions.

    Note: bc_x was computed using previousl tested methods.
    """
    P = Fd_problem((0, 1), (0, 1), equation, bo, (1), dx=0.2, dt=0.2, bc_map=bc_map)
    _, act_mat = P._implement_bc(np.zeros((size, size)), np.zeros(size), bc_x, True)
    act_mat = np.around(act_mat, decimals=2)
    print(act_mat)
    if check_type:
        assert np.all(act_mat == exp_mat)
    else:
        for elem in exp_mat:
            assert np.around(elem[2], decimals=1) == np.around(act_mat[elem[0], elem[1]], decimals=1)
