from utils import utils
import numpy as np
from scipy.sparse import diags
from scipy.linalg import solve
from plotting import animate_func

class Fd_problem:
    def __init__(
        self,
        domain,
        interval,
        boundary,
        initial,
        equation,
        dx,
        dt,
        time=["imp"],
        method=[("for", "cen"), ("for", "cen")],
    ):
        self.domain = domain
        self.equation = equation
        self.interval = interval
        self.boundary = boundary
        self.initial = initial
        self.method = method
        self.time = time
        self.dx = dx
        self.dt = dt

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

    def create_mesh(self):
        x0 = self.domain[0]
        xf = self.domain[1]
        Nx = int(np.round((xf - x0) / self.dx - 1))
        self.dx = (xf - x0) / (Nx + 1)
        return Nx

    def create_rhs(self, rhs_x, rhs_t, Nx):
        rhs_val = np.zeros(Nx)
        node_vals_t = rhs_t[1]
        for count, _ in enumerate(rhs_t[0]):
            rhs_val += np.ones(Nx) * self.initial[count] * node_vals_t[count]
        if rhs_x is not None:  # for explicit, not implemented yet
            pass
        return rhs_val

    def implement_bc(self, rhs, bc_x):
        node_vals_x = bc_x[1]
        for count, val in enumerate(bc_x[0]):
            val = int(val)
            if val == 0:
                continue
            elif val < 0:
                start = 0
                finish = -val - 1
                swap = 1
            else:
                start = 1
                finish = val
                swap = -1
            for idx in range(start, finish + 1):
                rhs[swap * idx] += node_vals_x[count] * self.boundary[count]
        return rhs

    def forward_in_time(self):
        mat_entries = utils._equ_to_exprlist(
            self.equation, self.method[0], self.method[1], self.dx, self.dt
        )
        mat, rhs_x, rhs_t, bc_x = utils._exprlist_to_mat(mat_entries, self.time)
        Nx = self.create_mesh()
        matrix = diags(mat[1], mat[0].astype(int), shape=(Nx, Nx)).toarray()
        mat_u = []
        for t in np.arange(self.interval[0], self.interval[1], self.dt):
            rhs = self.create_rhs(rhs_x, rhs_t, Nx)
            rhs = self.implement_bc(rhs, bc_x)
            u = solve(matrix, rhs)
            self.initial = u
            mat_u.append(u)
        animate_func(self.domain, self.dx, mat_u, self.boundary)
        return u
