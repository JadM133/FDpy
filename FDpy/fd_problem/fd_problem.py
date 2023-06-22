from FDpy.utils import utils
import numpy as np
from scipy.sparse import diags
from scipy.linalg import solve
from FDpy.plotting import start_animation


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
        self.dx = dx
        self.dt = dt
        self.Nx = self.create_mesh()
        self.boundary = [elem if isinstance(elem, tuple) else range(elem, elem + 1) for elem in boundary]
        self.initial = [np.ones(self.Nx)*elem if isinstance(elem, (int, float)) else elem for elem in initial]
        self.method = method
        self.time = time
        

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

    def create_rhs(self, rhs_x, rhs_t):
        rhs_val = np.zeros(self.Nx)
        node_vals_t = rhs_t[1]
        for count, _ in enumerate(rhs_t[0]):
            rhs_val += self.initial[count] * node_vals_t[count]
        if rhs_x is not None:  # for explicit, not implemented yet
            pass
        return rhs_val

    def implement_bc(self, matrix, rhs, bc_x, first):
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
                rhs[swap * idx] += node_vals_x[count] * self.boundary[count][0]
                if first:
                    for idx2 in range(len(self.boundary[count]) - 1):
                        new_idx = -(idx2+1) if swap == -1 else idx2
                        matrix[swap * idx, new_idx] += -node_vals_x[count] * self.boundary[count][idx2 + 1]
        return rhs

    def forward_in_time(self):
        mat_entries = utils._equ_to_exprlist(self.equation, self.method[0], self.method[1], self.dx, self.dt)
        mat, rhs_x, rhs_t, bc_x = utils._exprlist_to_mat(mat_entries, self.time)
        matrix = diags(mat[1], mat[0].astype(int), shape=(self.Nx, self.Nx)).toarray()
        mat_u = []
        first = True
        for t in np.arange(self.interval[0], self.interval[1], self.dt):
            rhs = self.create_rhs(rhs_x, rhs_t)
            rhs = self.implement_bc(matrix, rhs, bc_x, first)
            first = False
            u = solve(matrix, rhs)
            print(matrix)
            print(rhs)
            print(u)
            self.initial[0] = u
            mat_u.append(u)
        start_animation(self.domain, self.dx, mat_u, self.boundary)
        # totalfunc()
        return u
