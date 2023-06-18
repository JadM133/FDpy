def _compute_str_eq(coeffs, index):
    coeffs = coeffs[index]
    terms = []
    label = "x" if index == 0 else "t"
    terms += [
        None if coef == 0 else "{:+}".format(coef) + "U" + label * (idx+1)
        for idx, coef in enumerate(coeffs[2:])
    ]
    terms = '0' if terms == [] else terms
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
