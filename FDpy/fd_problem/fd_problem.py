"""Define class for a finite difference problem."""


from ..utils import utils
import numpy as np
from scipy.sparse import diags
from scipy.linalg import solve
from ..post_processing import start_animation
from collections import deque
from ..treenode import postvisitor, evaluate
from ..expressions import Expressions


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
        Boundary conditions (as much as the order requires). These can be given as
        a number, a tuple (representing the boundary points in function of inner points).
        Refer to README.md or sample_code.ipynb for more details.
    initial: list,
        Initial conditions (as much as the order requires). These can be given as constants,
        expressions (with x from the Expressions.Symbols class, name has to be 'x'), arrays
        (where every point is specified), or a tuple where we define an initial condition as
        a function of other initial conditions.
        (Refer to README.md or sample_code.ipynb for more details)
    equation: list,
        Equation to be solved specified by a list of two lists for LHS/RHS
        (see example in trail.ipynb).
    dx: float
        Mesh size
    dt: float,
        Time step
    method_fd: str,
        Method of finite difference, "imp" for implicit, "exp" for explicit.
        Note: Explicit schemes have not been heavily tested yet. Please use
        implicit schemes for guaranteed results.
    methods_xt: list of two str lists (check example for more details)
        Specifies methods for approx. derivatives ("for" for forward,
        "bac" for backward, "cen" for center) in both space/time.

    Methods
    -------
    forward_in_time(self, verbose=False, sanity=False, acc_x=2, acc_t=1):
        Use the problem defined and solves it on the time interval specified. The solution is returned
        in a form of matrix of points in space and time.
    post_process(self,mat_u,exact=None,reduce_frame=1,interval=300,xlabel="X",ylabel="U",label="Approx.",
                    exact_label="Exact",xlim=None,ylim=None,fps=30,save=False,
                    filename=None,error=False,anim=True,jup=False)
        FUnction for postprocessing (Mainly plotting animation and compare to exact solution). There is a
        lot of flexibility to chose properties of the animation (hence the large number of input arguments).
    """

    def __init__(
        self,
        domain: list,
        interval: list,
        equation: list,
        boundary=None,
        initial=None,
        dx=0.1,
        dt=0.1,
        method_fd="imp",
        method=["cen", "for"],
        bc_map=None,
    ):
        self.domain = domain
        self.equation = equation
        self.interval = interval
        self.dx = dx
        self.dt = dt
        if self.dx <= 0 or self.dt <= 0:
            raise ValueError(f"Increments can not be negative, specified dx = {self.dx} and dt = {self.dt}")
        if isinstance(boundary, (int, float)):
            self.boundary = [range(boundary, boundary + 1)]
        elif boundary is not None:
            self.boundary = [elem if isinstance(elem, tuple) else range(elem, elem + 1) for elem in boundary]
        else:
            self.boundary = None
        try:
            len(initial)
        except TypeError:
            if initial is not None:
                initial = [initial]
        if boundary is not None:
            self.Nx = self._create_mesh()
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
        self.bc_map = bc_map
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

    def _check_input(self, after=False):
        """Check if input given is in suitable shape/type."""
        if self.domain[0] >= self.domain[1]:
            raise ValueError("Provide domain in increasing order.")
        if len(self.domain) != 2:
            raise NotImplementedError("Only 1D domains implemented (len 2).")
        if self.interval[0] >= self.interval[1]:
            raise ValueError("Provide domain in increasing order.")
        if len(self.interval) != 2:
            raise ValueError("Interval must be of len 2")
        if self.initial is not None:
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
        if after:
            if self.bc_map is None or len(self.bc_map) != len(self.boundary):
                raise ValueError("Something went wrong with bc_map, did you provide it?")
            if len(self.equation[0]) < 2 or len(self.equation[1]) < 2:
                raise NotImplementedError("The equation needs to be at least first order in time and space.")
            for elem in self.boundary:
                if len(elem) >= self.Nx + 1:
                    raise ValueError("Boundary conditions can not depend on boundary conditions on the other side.")

    def _create_mesh(self):
        """Create a mesh by specifying start, end points and number of inner points."""
        x0 = self.domain[0]
        xf = self.domain[1]
        Nx = int(np.round((xf - x0) / self.dx - 1))
        self.dx = (xf - x0) / (Nx + 1)
        return Nx + (2 - len(self.boundary))

    def _create_rhs(self, rhs_x, rhs_t, bc_x, prev_times):
        """Create the rhs from previously computed values."""
        rhs_val = np.zeros(self.Nx)
        node_vals_t = rhs_t[1]
        for count in range(len(rhs_t[0])):
            rhs_val += prev_times[count] * node_vals_t[count]
        if rhs_x is not None:  # for explicit, not implemented yet
            node_vals_x = rhs_x[1]
            prev_at_m = prev_times[np.where(rhs_t[0] == 0)[0][0]]
            p = sum(bc_x[0] > 0)
            n = sum(bc_x[0] < 0)
            left_vals = []
            right_vals = []
            for idx in bc_x[0]:
                loc = idx + n if idx < 0 else idx - (p + 1)
                find = int(np.where(self.bc_map == loc)[0][0])
                if find == []:
                    raise ValueError(
                        "bc_map do not correspond to the right boundary conditions. Run self.info() for help."
                    )
                to_mult = self.boundary[find][0]
                for counter, dummy in enumerate(self.boundary[find][1:]):
                    count = counter if idx < 0 else -(counter + 1)
                    to_mult += dummy * prev_at_m[count]
                if idx < 0:
                    left_vals.append(to_mult)
                else:
                    right_vals.append(to_mult)
            prev_at_m = np.hstack((left_vals, prev_at_m, right_vals))
            for count, elem in enumerate(rhs_x[0]):
                elem = int(elem)
                end = -len(right_vals) + elem
                if end == 0:
                    rhs_val += prev_at_m[len(left_vals) + elem :] * node_vals_x[count]
                else:
                    rhs_val += prev_at_m[len(left_vals) + elem : -len(right_vals) + elem] * node_vals_x[count]
        return rhs_val

    def _implement_bc(self, matrix, rhs, bc_x, first):
        """Implement the boundary conditions by adding required entries to matrix/rhs."""
        node_vals_x = bc_x[1]
        for count, val in enumerate(bc_x[0]):
            val = int(val)
            p = sum(bc_x[0] > 0)
            n = sum(bc_x[0] < 0)
            if val == 0:
                continue
            elif val < 0:
                finish = -2
                start = -val - 1
                swap = 1
                chosen = n - 1
            else:
                start = val
                finish = -1
                swap = -1
                chosen = -p

            for idx in range(start, finish + 1, -1):
                find = np.where(self.bc_map == chosen)[0][0]
                try:
                    rhs[swap * idx] += node_vals_x[count] * self.boundary[find][0]
                except IndexError:
                    raise ValueError("Wrong BCs were provided, did you provide a bc_map?")
                if first:
                    for idx2 in range(len(self.boundary[find]) - 1):
                        new_idx = -(idx2 + 1) if swap == -1 else idx2
                        matrix[swap * idx, new_idx] += -node_vals_x[count] * self.boundary[find][idx2 + 1]
                chosen += -swap
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

    def info(self, acc_x=2, acc_t=1):
        """Provide Information about boundary/initial conditions needed."""
        bc_x, rhs_t, expr_x, expr_t = self.forward_in_time(acc_x=acc_x, acc_t=acc_t, sanity=True)
        p = int(sum(bc_x[0] > 0))
        n = int(sum(bc_x[0] < 0))
        p_vec = np.arange(-p, 0)
        n_vec = np.arange(0, n)
        keys_t = rhs_t[0]
        print("****************SUMMARY**************")
        print(f"Left hand side: {expr_x}")
        print(f"with accuracy: {acc_x}")
        print(f"Right hand side: {expr_t}")
        print(f"with accuracy: {acc_t}")
        print(f"BC are needed at the following points from the right: {p_vec}")
        print(f"And these from the left: {n_vec}")
        print(f"IC are needed at the following times: {keys_t}")
        return p_vec, n_vec, keys_t

    def add(self, boundary=None, initial=None, bc_map=None):
        """Allow the user to give bc and ic not previosuly specified when initializing.

        Note: This is useful if the user wants to use the function self.info() to know
        which boundary/initial conditions are needed.
        """
        if isinstance(boundary, (int, float)):
            self.boundary = [range(boundary, boundary + 1)]
        elif boundary is not None:
            self.boundary = [elem if isinstance(elem, tuple) else range(elem, elem + 1) for elem in boundary]
        try:
            len(initial)
        except TypeError:
            if initial is not None:
                initial = [initial]
        self.Nx = self._create_mesh()
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
        self.bc_map = bc_map
        self._check_input(after=True)

    def forward_in_time(self, verbose=False, sanity=False, acc_x=2, acc_t=1):
        """Step in time to find solution at all times."""
        mat_entries, expr_x, expr_t = utils._equ_to_exprlist(
            self.equation,
            acc_x,
            acc_t,
            self.method[0],
            self.method[1],
            self.dx,
            self.dt,
            time=self.method_fd,
            verbose=verbose,
        )
        mat, rhs_x, rhs_t, bc_x = utils._exprlist_to_mat(mat_entries, self.method_fd)

        if sanity:
            return bc_x, rhs_t, expr_x, expr_t
        if len(self.boundary) != len(bc_x[0]):
            raise ValueError("Wrong number of boundary conditions. Run self.bc_info for more details.")
        if len(self.initial) != len(rhs_t[0]):
            raise ValueError("Wrong number of initial conditions. Run self.bc_info for more details.")

        matrix = diags(mat[1], mat[0].astype(int), shape=(self.Nx, self.Nx)).toarray()
        first = True
        prev_times = deque(self._init_rhs())
        mat_u = []
        mat_u.append(prev_times[0])
        print("Solving the matrix system for all times...")
        for _ in np.arange(
            self.interval[0] + self.dt * (len(self.equation[1]) - 2), self.interval[1] + self.dt, self.dt
        ):
            rhs = self._create_rhs(rhs_x, rhs_t, bc_x, prev_times)
            if self.method_fd == "imp":
                rhs, matrix = self._implement_bc(matrix, rhs, bc_x, first)
            first = False
            u = solve(matrix, rhs)
            prev_times.append(u)
            prev_times.popleft()
            mat_u.append(u)
        self.solution = mat_u
        print("Done.")
        return mat_u

    def post_process(
        self,
        mat_u,
        exact=None,
        interval=300,
        xlabel="X",
        ylabel="U",
        label="Approx.",
        exact_label="Exact",
        xlim=None,
        ylim=None,
        fps=30,
        save=True,
        filename=None,
        error=False,
        anim=True,
        jup=False,
    ):
        """Plot the solution for all times in a GIF."""
        return start_animation(
            domain=self.domain,
            time_interval=self.interval,
            dx=self.dx,
            dt=self.dt,
            u_mat=mat_u,
            exact=exact,
            boundary=self.boundary,
            bc_map=self.bc_map,
            interval=interval,
            xlabel=xlabel,
            ylabel=ylabel,
            label=label,
            exact_label=exact_label,
            xlim=xlim,
            ylim=ylim,
            fps=fps,
            save=save,
            filename=filename,
            error=error,
            anim=anim,
            jup=jup,
        )
