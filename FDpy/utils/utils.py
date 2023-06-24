from FDpy.expressions import Symbol
from FDpy.expressionlist import ExpressionList
import numpy as np


def _compute_str_eq(coeffs, index):
    coeffs = coeffs[index]
    terms = []
    label = "x" if index == 0 else "t"
    terms += [
        None if coef == 0 else "{:+}".format(coef) + "U" + label * (idx + 1) for idx, coef in enumerate(coeffs[2:])
    ]
    terms = "0" if terms == [] else terms
    terms = list(filter(lambda item: item is not None, terms))
    terms = " ".join(reversed(terms))
    return terms


def _compute_str_cond(domain, boundary, idx):
    bc_str = []
    try:
        length = len(boundary)
        bc_str += ["U = " + str(boundary[i]) + " at " + idx + " = " + str(domain[i]) for i in range(length)]
        bc_str = ", ".join(bc_str)
    except TypeError:
        length = 1
        bc_str = "U = " + str(boundary) + " at " + idx + " = " + str(domain[0])

    idx = "BC: " if idx == "x" else "IC: "
    bc_str = idx + bc_str
    return bc_str


def _sum_sides(equation, idx):
    constant = equation[0][idx] - equation[1][idx]
    constant = " " + "{:+}".format(constant) if constant != 0 else ""
    if idx == 1 and constant != "":
        constant += "U"
    return constant


def _x_or_t_to_epxrlist(equation, methods, step_size):
    """
    Convert one part of an Fd_problem equation to an ExpressionList.

    Parameters
    ----------
    equation part : (0, ..., 1, 3) array_like
        Equation part to be converted.

    methods : ["method1", "method2"] list_like
        Specifies the method for computing derivatives: "for" 
        for forward, "bac" for backward, and "cen" for center.
        The first entry is for the first derivative, the 
        second entry is for all higher derivatives.

    step_size : float
        Specifies the step size in etiher x or t.

    Returns
    -------
    sum_n : ExpressionList instance
        Returns an ExpressionList instance with info about how to fill 
        matrix/rhs for all n derivatives>

    Examples
    --------
    Equation part uxx, given as (0, 0, 0, 1):
    >>> equation = (0, 0, 0, 1)
    >>> utils._x_or_t_to_epxrlist(equation, ["for", "cen"], 0.1)
    ExpressionList{0: -200.0, 1: 100.0, -1: 100.0}
    Where the keys specify the position wrt the diagonal of a matrix 
    (i.e. 0 for diagonal, 1 for line above diagonal, -1 for line below, ...)
    and the values specify what should be added to the matrix (e.g. -2/dx**2,
    and 1/dx**2 for center approximation in x in this case).
    Note: the first entry of methods is not used in this case since there is
    no first derivatives in the equation specified.
    """
    res_list = []

    res_list.append(ExpressionList({0: equation[1]}))
    inc = Symbol("inc")

    ux_back = ExpressionList({0: 1 / inc, -1: -1 / inc})
    ux_for = ExpressionList({1: 1 / inc, 0: -1 / inc})
    ux_cen = ExpressionList({1: 1 / (2 * inc), -1: -1 / (2 * inc)})

    if methods[0] == "for":
        res_list.append(ux_for * equation[2])
    elif methods[0] == "bac":
        res_list.append(ux_back * equation[2])
    elif methods[0] == "cen":
        res_list.append(ux_cen * equation[2])
    else:
        raise NotImplementedError(f"Method {methods[0]} not implemented for first derivatives")

    u_n_minus_1_for = ux_for
    u_n_minus_1_bac = ux_back

    for n in range(len(equation) - 3):
        u_n_for = (u_n_minus_1_for.inc() - u_n_minus_1_for) / inc
        u_n_bac = (u_n_minus_1_bac - u_n_minus_1_bac.dec()) / inc
        u_n_cen = (u_n_minus_1_for - u_n_minus_1_bac) / inc

        if methods[1] == "for":
            res_list.append(u_n_for * equation[n + 3])
        elif methods[1] == "bac":
            res_list.append(u_n_bac * equation[n + 3])
        elif methods[1] == "cen":
            res_list.append(u_n_cen * equation[n + 3])
        else:
            raise NotImplementedError

        u_n_minus_1_for = u_n_for
        u_n_minus_1_bac = u_n_bac

    for idx in range(len(res_list)):
        if idx == 0:
            sum_n = res_list[idx]
        else:
            sum_n += res_list[idx]
    sum_n = sum_n(step_size, inc)
    return sum_n


def _equ_to_exprlist(equation, method_x=["for", "for"], method_t=["for", "for"], dx_val=0.1, dt_val=0.1):
    """
    Convert an Fd_problem equation to an ExpressionList.

    Parameters
    ----------
    equation : ((0, ..., 1, 3), (2, ..., 0)) array_like
        Equation to be converted.

    method_x : ["method1", "method2"] list_like
        Specifies the method for computing derivatives in x,"for" 
        for forward, "bac" for backward, and "cen" for center.
        The first entry is for the first derivative, the 
        second entry is for all higher derivatives.

    method_t : ["method1", "method2"] list_like
        Specifies the method for computing derivatives in t,"for" 
        for forward, "bac" for backward, and "cen" for center.
        THhe first entry is for the first derivative, the 
        second entry is for all higher derivatives.

    dx_val : float
        Specifies the mesh size in x.

    dt_val : float
        Specifies the step size in t.

    Returns
    -------
    mat_x : np array
        Returns an ExpressionList instance with info about how to fill 
        matrix/rhs for the x-part of the equation.

    mat_t : np array
        Returns an ExpressionList instance with info about how to fill 
        matrix/rhs for the x-part of the equation.

    Examples
    --------
    Equation ux = ut, given as ((0, 0, 1), (0, 0, 1)):
    >>> equation = ((0, 0, 1), (0, 0, 1))
    >>> utils._equ_to_exprlist(equation, ["cen"], ["for"], 0.1, 0.1)
    (ExpressionList{1: 5.0, -1: -5.0}, ExpressionList{0: -10.0, 1: 10.0})
    Where the keys specify the position wrt the diagonal of a matrix 
    (i.e. 0 for diagonal, 1 for line above diagonal, -1 for line below, ...)
    and the values specify what should be added to the matrix (e.g. 1/2dx,
    and -1/2dx for center approximation in x in this case).
    """
    mat_x = _x_or_t_to_epxrlist(equation[0], method_x, dx_val)
    mat_t = _x_or_t_to_epxrlist(equation[1], method_t, dt_val)
    return mat_x, mat_t


def _exprlist_to_mat(mat_entries, time="imp"):
    x_entries, t_entries = mat_entries
    mat_dict, rhs_x, rhs_t, bc_x = x_entries.combine_x_and_t(t_entries, time)
    mat_array = np.transpose(np.array(list(mat_dict.items())))
    rhs_t = np.transpose(np.sort(np.array(list(rhs_t.items())), axis=0))
    if rhs_x is not None:
        rhs_x = np.transpose(np.sort(np.array(list(rhs_x.items())), axis=0))
    bc_x = np.transpose(np.sort(np.array(list(bc_x.items())), axis=0))
    return mat_array, rhs_x, rhs_t, bc_x


res = _x_or_t_to_epxrlist((1, 2, 1, 1), ["bac", "cen"], 0.1)
