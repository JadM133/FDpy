from expressions import Symbol
from expressionlist import ExpressionList


def _compute_str_eq(coeffs, index):
    coeffs = coeffs[index]
    terms = []
    label = "x" if index == 0 else "t"
    terms += [
        None if coef == 0 else "{:+}".format(coef) + "U" + label * (idx + 1)
        for idx, coef in enumerate(coeffs[2:])
    ]
    terms = "0" if terms == [] else terms
    terms = list(filter(lambda item: item is not None, terms))
    terms = " ".join(reversed(terms))
    return terms


def _compute_str_cond(domain, boundary, idx):
    bc_str = []
    try:
        length = len(boundary)
        bc_str += [
            "U = " + str(boundary[i]) + " at " + idx + " = " + str(domain[i])
            for i in range(length)
        ]
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


def _equ_to_exprlist(equation, methods=["for", "for"]):
    res_list = []
    equation_x = equation[0]
    res_list.append(ExpressionList({1: equation_x[1]}))
    dx = Symbol("dx")

    ux_back = ExpressionList({0: 1 / dx, -1: -1 / dx})
    ux_for = ExpressionList({1: 1 / dx, 0: -1 / dx})
    ux_cen = ExpressionList({1: 1 / (2 * dx), -1: -1 / (2 * dx)})

    if methods[0] == "for":
        res_list.append(ux_for*equation_x[2])
    elif methods[0] == "bac":
        res_list.append(ux_back*equation_x[2])
    elif methods[0] == "center":
        res_list.append(ux_cen*equation_x[2])
    else:
        raise NotImplementedError(
            f"Method {methods[0]} not implemented for first derivatives"
        )

    u_n_minus_1_for = ux_for
    u_n_minus_1_bac = ux_back

    for n in range(len(equation[0]) - 3):
        u_n_for = (u_n_minus_1_for.inc() - u_n_minus_1_for) / dx
        u_n_bac = (u_n_minus_1_bac - u_n_minus_1_bac.dec()) / dx
        u_n_cen = (u_n_minus_1_for - u_n_minus_1_bac) / dx

        if methods[1] == "for":
            res_list.append(u_n_for*equation_x[n+3])
        elif methods[1] == "bac":
            res_list.append(u_n_bac*equation_x[n+3])
        elif methods[1] == "center":
            res_list.append(u_n_cen*equation_x[n+3])
        else:
            raise NotImplementedError

        u_n_minus_1_for = u_n_for
        u_n_minus_1_bac = u_n_bac

    for idx in range(len(res_list)):
        if idx == 0:
            sum_n = res_list[idx]
        else:
            sum_n += res_list[idx]
    sum_n = sum_n(dx=0.1)
    print(sum_n)
