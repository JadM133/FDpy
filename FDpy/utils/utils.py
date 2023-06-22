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


def _equ_to_exprlist(equation, method_x=["for", "for"], method_y=["for", "for"], dx_val=0.1, dt_val=0.1):
    mat_x = _x_or_t_to_epxrlist(equation[0], method_x, dx_val)
    mat_y = _x_or_t_to_epxrlist(equation[1], method_y, dt_val)
    return mat_x, mat_y


def _exprlist_to_mat(mat_entries, time="imp"):
    x_entries, t_entries = mat_entries
    mat_dict, rhs_x, rhs_t, bc_x = x_entries.combine_x_and_t(t_entries, time)
    mat_array = np.transpose(np.array(list(mat_dict.items())))
    rhs_t = np.transpose(np.sort(np.array(list(rhs_t.items())), axis=0))
    if rhs_x is not None:
        rhs_x = np.transpose(np.sort(np.array(list(rhs_x.items())), axis=0))
    bc_x = np.transpose(np.sort(np.array(list(bc_x.items())), axis=0))
    return mat_array, rhs_x, rhs_t, bc_x
