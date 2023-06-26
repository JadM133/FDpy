
"""Module containing all utility functions that will be used by other defined classes."""


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


def _compute_coefficients(accuracy, order, points, x0=0):
    """Implement Bengt Fornberg algorythm to find coefficients of FD."""
    coeffs = np.zeros((accuracy + 1, accuracy + 1, min(order, accuracy) + 1))
    coeffs[0, 0, 0] = 1
    c1 = 1
    for n in range(accuracy):
        nt = n + 1
        c2 = 1
        for nu in range(nt):
            c3 = points[nt] - points[nu]
            c2 = c2 * c3
            for m in range(min(nt, order) + 1):
                if m == 0:
                    coeffs[nt, nu, m] = ((points[nt] - x0) * coeffs[nt - 1, nu, m]) / c3
                else:
                    coeffs[nt, nu, m] = ((points[nt] - x0) * coeffs[nt - 1, nu, m] - m * coeffs[nt - 1, nu, m - 1]) / c3
        for m in range(min(nt, order) + 1):
            if m == 0:
                coeffs[nt, nt, m] = c1 / c2 * (-(points[nt - 1] - x0) * coeffs[nt - 1, nt - 1, m])
            else:
                coeffs[nt, nt, m] = (
                    c1 / c2 * (m * coeffs[nt - 1, nt - 1, m - 1] - (points[nt - 1] - x0) * coeffs[nt - 1, nt - 1, m])
                )
        c1 = c2
    return coeffs


def _to_exprlist(coeffs_at_order, points, name, step_size, time="imp", order_t=None):
    """Convert coefficients into expression and sorted dict.

    Returns
    -------
    expr : Expression instance
        This can be used to print the aproximation in a nice way.
    dic : ExpressionList instance with dict as atrribute.
        Keys: values where keys sopecify on which diagonal of the matrix
        the values should later be.
    dic.max_key(): int
        the largest key in dic. This will be used to specify at which
        time the U values are evaluated in the implicit scheme.
    """
    h = Symbol(name)
    dic = {}
    symb_ls = []
    for idx in range(len(points)):
        if name == "dx":
            name1 = points[idx]
            if name1 == 0:
                name1 = ""
            else:
                name1 = "{:+}".format(name1)
            if time == "imp":
                name2 = order_t
                if name2 == 0:
                    name2 = ""
                else:
                    name2 = "{:+}".format(name2)
            else:
                name2 = ""
            symb_ls.append(Symbol(f"U(i{name1},j{name2})"))
        else:
            name1 = ""
            name2 = points[idx]
            if name2 == 0:
                name2 = ""
            else:
                name2 = "{:+}".format(name2)
            symb_ls.append(Symbol(f"U(i,j{name2})"))
    for der, idx in enumerate(range(len(coeffs_at_order))):
        vec_at_idx = coeffs_at_order[idx]
        expr_idx = 0
        for count, elem in enumerate(vec_at_idx):
            if elem != 0:
                expr_idx += np.around(elem, decimals=2) * symb_ls[count]
        if der != 0:
            expr_idx /= h**der
            dic += ExpressionList({k: v for k, v in zip(points, vec_at_idx / h**der)})
        else:
            dic = ExpressionList({k: v for k, v in zip(points, vec_at_idx)})
            expr = 0
        if expr_idx != 0:
            expr += expr_idx
    dic = dic(step_size, name)
    return expr, dic, dic.max_key()


def _x_or_t_to_epxr(equation, method, name, step_size, acc=2, time="imp", order_t=None):
    """Transform one side of the equation to an expression and dict.

    This function is divided into 3 main parts. First, specifying required
    values for Bengt Fornberg algorythm (ref in Readme file). Second applying
    the algorythm and extracting the needed values from there. Last transforming
    these into Expression/Expressionlist which will be useful later.

    See Also
    --------
    _to_expr : Third step is explained further.
    """
    order = len(equation) - 2
    if acc < order:
        accuracy = order + 2  # Accuracy should be big enough
    else:
        accuracy = acc + order
    points = []
    points.append(0)
    if method == "cen":
        for p in range(1, np.round(accuracy)):
            points.append(p)
            points.append(-p)
    elif method == "for":
        for p in range(1, np.round(2 * accuracy)):
            points.append(p)
    elif method == "bac":
        for p in range(-1, -np.round(2 * accuracy), -1):
            points.append(p)

    coeffs = _compute_coefficients(accuracy, order, points)
    coeffs_at_order = []  # Extract only coefficients at required order
    for der in range(order + 1):
        start = np.nonzero(coeffs[:, :, der])[0][0]
        coeffs_at_order.append(coeffs[start + acc - 1, :, der] * equation[der + 1])
    expr, coeffs, order_t = _to_exprlist(coeffs_at_order, points, name, step_size, time, order_t=order_t)
    return expr, coeffs, order_t


def _equ_to_expr(equation, acc_x, acc_t, method_x=["cen"], method_t=["for"], dx_val=0.1, dt_val=0.1, time="imp", verbose=True):
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
    coeffs_x : np array
        ExpressionList instance with info about how to fill
        matrix/rhs for the x-part of the equation.

    coeffs_t : np array
        ExpressionList instance with info about how to fill
        matrix/rhs for the t-part of the equation.

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
    expr_t, coeffs_t, order_t = _x_or_t_to_epxr(equation[1], method_t, "dt", dt_val, acc=acc_t, time=time)
    expr_x, coeffs_x, _ = _x_or_t_to_epxr(equation[0], method_x, "dx", dx_val, acc=acc_x, time=time, order_t=order_t)
    if verbose:
        print("*******************Approximation*****************")
        print(f"Left hand side: {expr_x}")
        print(f"Right hand side: {expr_t}")
        print("Where U(i, j) means at point x = i*delta x and t = j * delta t")
    return [coeffs_x, coeffs_t], expr_x, expr_t


def _exprlist_to_mat(mat_entries, time="imp"):
    """Transform two dicts into arrays to fill the matrix/rhs later.

    In this function, we only take care of having the right type. The
    bulk of the transformation happening is in combine_x_and_t.

    See Also
    --------
    class ExpressionList : Detailed explanation/examples of combine_x_and_t.
    """
    x_entries, t_entries = mat_entries
    mat_dict, rhs_x, rhs_t, bc_x = x_entries.combine_x_and_t(t_entries, time)
    mat_array = np.transpose(np.array(list(mat_dict.items())))
    rhs_t = np.transpose(np.sort(np.array(list(rhs_t.items())), axis=0))
    if rhs_x is not None:
        rhs_x = np.transpose(np.sort(np.array(list(rhs_x.items())), axis=0))
    bc_x = np.transpose(np.sort(np.array(list(bc_x.items())), axis=0))
    return mat_array, rhs_x, rhs_t, bc_x
