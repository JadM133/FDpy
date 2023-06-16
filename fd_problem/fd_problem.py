import utils


class Fd_problem:
    def __init__(
        self, domain, interval, boundary, initial, method, equation, dx=0.01, dt=0.01
    ):
        self.domain = domain
        self.equation = equation
        self.interval = interval
        self.boundary = boundary
        self.initial = initial
        self.method = method
        self.inc_x = dx
        self.inc_t = dt

    def __str__(self):
        constant = self.equation[0][0] - self.equation[1][0]
        constant = " " + "{:+}".format(constant) if constant != 0 else ""
        x_terms = utils._compute_str_eq(self.equation, 0)
        t_terms = utils._compute_str_eq(self.equation, 1)
        eq_str = "Equation: " + x_terms + constant + " = " + t_terms

        bc_str = utils._compute_str_cond(self.domain, self.boundary, "x")

        ic_str = utils._compute_str_cond(self.interval, self.initial, "t")

        return ", \n".join([eq_str, bc_str, ic_str]) + "."


A = Fd_problem((0, 1), (0, 5), (0, 0), (1), "Imp", ((1, -1, 0, 4, 5, 0, 10), (2, 0, 1)))
print(A)
