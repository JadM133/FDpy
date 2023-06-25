"""Define class for a finite difference problem."""


from FDpy.utils import utils
import numpy as np
from scipy.sparse import diags
from scipy.linalg import solve
from FDpy.plotting import start_animation
from collections import deque
from FDpy.treenode import postvisitor, evaluate
from FDpy.expressions import Expressions


class Fd_problem:
    """
    A class to represent a finite difference problem.

    Parameters
    ----------
    domain: list,
        Domain (1D), specified by two points.
    interval: list,
        Start/end times.
    boundary: list,
        Boundary conditions (as much as the order requires).
    initial: list,
        Initial conditions (as much as the order requires).
    equation: list,
        Equation to be solved specified by a list of two lists for LHS/RHS (see example).
    dx: float
        Mesh size in the x-direction
    dt: float,
        Time step
    method_fd: str,
        Method of finite difference, "imp" for implicit, "exp" for explicit.
    methods_xt: list of two str lists (check example for more details)
        Specifies methods for approx. derivatives ("for" for forward,
        "bac" for backward, "cen" for center) in both space/time.

    Methods
    -------
    __str__(self):
        Return string representaion of the equaotion of the Fdproblem instance.
    forward_in_time():
    """

    def __init__(
        self,
        domain: list,
        interval: list,
        boundary: list,
        initial: list,
        equation: list,
        dx=0.1,
        dt=0.1,
        method_fd="imp",
        method=["cen", "for"],
    ):
        self.domain = domain
        self.equation = equation
        self.interval = interval
        self.dx = dx
        self.dt = dt
        if self.dx <= 0 or self.dt <= 0:
            raise ValueError(f"Increments can not be negative, specified dx = {self.dx} and dt = {self.dt}")
        self.Nx = self._create_mesh()
        if isinstance(boundary, (int, float)):
            self.boundary = [boundary]
        elif boundary is not None:
            self.boundary = [elem if isinstance(elem, tuple) else range(elem, elem + 1) for elem in boundary]
        else:
            self.boundary = None
        try:
            len(initial)
        except TypeError:
            if initial is not None:
                initial = [initial]
        if initial is not None:
            self.initial = [np.ones(self.Nx) * elem if isinstance(elem, (int, float)) else elem for elem in initial]
            self.initial = [
                postvisitor(
                    elem,
                    evaluate,
                    symbol_map={"x": np.linspace(self.domain[0] + self.dx, self.domain[1] - self.dx, self.Nx)},
                )
                if isinstance(elem, Expressions)
                else elem
                for elem in self.initial
            ]
        else:
            self.initial = None
        self.method = method
        self.method_fd = method_fd
        self._check_input()
        self.solution = []

    def __str__(self):
        """Return string representation of the equation to be solved."""
        constant = utils._sum_sides(self.equation, 0)
        U_term = utils._sum_sides(self.equation, 1)

        x_terms = utils._compute_str_eq(self.equation, 0)
        t_terms = utils._compute_str_eq(self.equation, 1)
        eq_str = "Equation: " + x_terms + U_term + constant + " = " + t_terms

        return eq_str

    def _check_input(self):
        """Check if input given is in suitable shape/type."""
        if self.domain[0] >= self.domain[1]:
            raise ValueError("Provide domain in increasing order.")
        if len(self.domain) != 2:
            raise NotImplementedError("Only 1D domains implemented (len 2).")
        if self.interval[0] >= self.interval[1]:
            raise ValueError("Provide domain in increasing order.")
        if len(self.interval) != 2:
            raise ValueError("Interval must be of len 2")
        if self.boundary is not None and len(self.boundary) != len(self.equation[0]) - 2:
            raise ValueError(f"Wrong number of boundary conditions, expected {len(self.equation[0])-2}.")
        if self.initial is not None:
            if len(self.initial) != len(self.equation[1]) - 2:
                raise ValueError(f"Wrong number of initial conditions, expected {len(self.equation[1])-2}.")
            for elem in self.initial:
                if not isinstance(elem, np.ndarray) and not isinstance(elem, tuple):
                    raise NotImplementedError("Initial conditions must be of a number or of types: tuple, np.ndarray.")
                if isinstance(elem, np.ndarray) and elem.shape != (self.Nx,):
                    raise ValueError(
                        f"If initial condition specified as array, please specify it at every point (size of {self.Nx})."
                    )
                elif isinstance(elem, tuple) and len(elem) > len(self.initial) + 1:
                    raise NotImplementedError(f"Initial conditions can not depend on element {len(elem)-1} (unknown).")
        if (self.equation[0])[-1] == 0 or (self.equation[1])[-1] == 0:
            raise ValueError("0 is not expected as last entry, did you write the equation in the right way?")
        if self.method_fd != "imp" and self.method_fd != "exp":
            raise NotImplementedError(f"Only imp and exp are imlemented as method_fd, not {self.method_fd}.")
        if len(self.method) != 2:
            raise ValueError("Method should be an array of strings of length 2. Do not specify for default option.")
        if self.method[0] != "for" and self.method[0] != "bac" and self.method[0] != "cen":
            raise ValueError("Entry 0 of method can only be for, bac, or cen in a string.")
        if self.method[1] != "for" and self.method[1] != "bac" and self.method[1] != "cen":
            raise ValueError("Entry 1 of method can only be for, bac, or cen in a string.")

    def _create_mesh(self):
        """Create a mesh by specifying start, end points and number of inner points."""
        x0 = self.domain[0]
        xf = self.domain[1]
        Nx = int(np.round((xf - x0) / self.dx - 1))
        self.dx = (xf - x0) / (Nx + 1)
        return Nx

    def _create_rhs(self, rhs_x, rhs_t, prev_times):
        """Create the rhs from previously computed values."""
        rhs_val = np.zeros(self.Nx)
        node_vals_t = rhs_t[1]
        for count in range(len(rhs_t[0])):
            rhs_val += prev_times[count] * node_vals_t[count]
        if rhs_x is not None:  # for explicit, not implemented yet
            pass
        return rhs_val

    def _implement_bc(self, matrix, rhs, bc_x, first):
        """Implement the boundary conditions by adding required entries to matrix/rhs."""
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
                        new_idx = -(idx2 + 1) if swap == -1 else idx2
                        matrix[swap * idx, new_idx] += -node_vals_x[count] * self.boundary[count][idx2 + 1]
        return rhs, matrix

    def _init_rhs(self):
        """Transform the initial conditions to the rhs of the matrix system."""
        res = np.zeros((len(self.initial), self.Nx))
        for point in range(self.Nx):
            M = np.diag(np.ones(len(self.initial)))
            b = np.zeros(len(self.initial))
            for count, elem in enumerate(self.initial):
                if isinstance(elem, np.ndarray):
                    b[count] = elem[point]
                elif isinstance(elem, tuple):
                    b[count] = elem[0]
                    for count2, elem2 in enumerate(elem[1:]):
                        M[count, count2] += -elem2
            try:
                x = np.linalg.solve(M, b)
            except ValueError:
                raise ValueError("Initial conditions are not enough. Did you provide independent equations?")
            res[:, point] = x
        return res

    def forward_in_time(self, verbose=True):
        mat_entries = utils._equ_to_expr(
            self.equation, self.method[0], self.method[1], self.dx, self.dt, time=self.method_fd, verbose=verbose
        )
        mat, rhs_x, rhs_t, bc_x = utils._exprlist_to_mat(mat_entries, self.method_fd)
        matrix = diags(mat[1], mat[0].astype(int), shape=(self.Nx, self.Nx)).toarray()
        mat_u = self.initial  # Matrix that will store results for all time.
        first = True
        prev_times = deque(self._init_rhs())
        for _ in np.arange(self.interval[0] + self.dt * (len(self.equation[1]) - 2), self.interval[1], self.dt):
            rhs = self._create_rhs(rhs_x, rhs_t, prev_times)
            rhs, matrix = self._implement_bc(matrix, rhs, bc_x, first)
            first = False
            u = solve(matrix, rhs)
            prev_times.append(u)
            prev_times.popleft()
            mat_u.append(u)
        self.solution = mat_u
        start_animation(self.domain, self.dx, mat_u, self.boundary)
        return mat_u
