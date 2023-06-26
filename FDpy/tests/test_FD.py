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
    P = Fd_problem((0, 1), (0, 1), (0, 0), initial, equation, dx=0.2, dt=0.2)
    res = np.around(P._init_rhs().tolist(), decimals=1)
    assert np.all(res == act_res), f"RHS is wrong, expected{act_res} but got {act_res}"


@pytest.mark.parametrize(
    "bo, equation, bc_x, bc_map, exp_rhs",
    [
        (1, ((0, 0, 1), (0, 0, 1)), np.array([[1], [5]]), [-1], [0, 0, 0, 5]),
        (1, ((0, 0, 1), (0, 0, 1)), np.array([[-1], [-5]]), [0], [-5, 0, 0, 0]),
        ([(1, 1, 2, 3)], ((0, 0, 1), (0, 0, 1)), np.array([[-1], [-5]]), [0], [-5, 0, 0, 0]),
        ((1, 1), ((0, 0, 0, 1), (0, 0, 1)), np.array([[-1, 1], [25, 25]]), [0, -1], [25, 0, 0, 25]),
        (
            (1, 1, 2),
            ((0, 0, 0, 0, 1), (0, 0, 1)),
            np.array([[-1, 1, 2], [-375, -125, 125]]),
            [0, -1, -2],
            [-375, 0, 250, -125],
        ),
    ],
)
def test_implement_bc_rhs(bo, equation, bc_x, bc_map, exp_rhs):
    """Test if boundary conditions are implemented properly in the rhs.

    Note: the values of bc_x corresponding to the functions were computed
    manually using previously tested functions.

    Note: bc_x was computed using previousl tested methods.
    """
    P = Fd_problem((0, 1), (0, 1), bo, (1), equation, dx=0.2, dt=0.2, bc_map=bc_map)
    act_rhs, _ = P._implement_bc(np.zeros((4, 4)), np.zeros(4), bc_x, False)
    assert np.all(act_rhs.tolist() == exp_rhs)


bo, equation, bc_x, bc_map = (
    (1, 1, 2),
    ((0, 0, 0, 0, 1), (0, 0, 1)),
    np.array([[-1, 1, 2], [-375, -125, 125]]),
    [0, -2, -1],
)
P = Fd_problem((0, 1), (0, 1), bo, (1), equation, dx=0.2, dt=0.2, bc_map=bc_map)
act_rhs, _ = P._implement_bc(np.zeros((4, 4)), np.zeros(4), bc_x, False)
# @pytest.mark.parametrize(
#     "bo, equation, bc_x, exp_mat, check_type",
#     [
#         ([(1, 1, 2, 3)], ((0, 0, 1), (0, 0, 1)), [[1], [-5]], [(3, 3, 5), (3, 2, 10), (3, 1, 15)], 0),
#         ((1, 1, 2), ((0, 0, 0, 0, 1), (0, 0, 1)), [[-1, 1, 2], [-375, -125, 125]], np.zeros((4, 4)), 1),
#         [(1, 1), (0, 2, 1), 3], ((0, 0, 0, 1), (0, 0, 1)), [[1, 2, 3], [-125, -25, 100]], [(3, 3, -125), (2, 3, -25)]
#     ],
# )
# def test_implement_bc_mat(bo, equation, bc_x, exp_mat, check_type):
#     """Test if boundary conditions are implemented properly in the rhs.

#     Note: the values of bc_x corresponding to the functions were computed
#     manually using previously tested functions.

#     Note: bc_x was computed using previousl tested methods.
#     """
#     P = Fd_problem((0, 1), (0, 1), bo, (1), equation, dx=0.2, dt=0.2)
#     _, act_mat = P._implement_bc(np.zeros((4, 4)), np.zeros(4), bc_x, True)
#     print(act_mat)
#     if check_type:
#         assert np.all(act_mat == exp_mat)
#     else:
#         for elem in exp_mat:
#             assert elem[2] == act_mat[elem[0], elem[1]]
