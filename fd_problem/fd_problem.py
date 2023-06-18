from utils import utils


class Fd_problem:
    def __init__(self, domain, interval, boundary, initial, method, equation):
        self.domain = domain
        self.equation = equation
        self.interval = interval
        self.boundary = boundary
        self.initial = initial
        self.method = method

    def __str__(self):
        constant = utils._sum_sides(self.equation, 0)
        U_term = utils._sum_sides(self.equation, 1)

        x_terms = utils._compute_str_eq(self.equation, 0)
        t_terms = utils._compute_str_eq(self.equation, 1)
        eq_str = "Equation: " + x_terms + U_term + constant + " = " + t_terms

        bc_str = utils._compute_str_cond(self.domain, self.boundary, "x")

        ic_str = utils._compute_str_cond(self.interval, self.initial, "t")

        method_str = "Method: Implicit Finite Differences"

        return ", \n".join([eq_str, bc_str, ic_str, method_str]) + "."

    # def forward_in_time(self, dx=0.01, dt=0.01):
