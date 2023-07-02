
"""Define ExpressionList class which provides useful methods to create matrix/rhs."""


from ..treenode import postvisitor, evaluate
from ..expressions import Symbol
import numpy as np


class ExpressionList:
    """
    A class to help in creating the matrix/rhs from a linear partial differential equation.

    The only parameter specifies the position in the matrix and corresponding value (read
    parameters for further info). Even though this class only contains one attribute, it
    allows us to define unique properties (e.g. add, mul, ...) which make sense in this
    case (more details in Methods).

    Parameters
    ----------
    expr_dict: dict
        A dictionary which defines an expression and how it should be filled in a matrix.
        The keys specify the position wrt the diagonal (0 for diagonal, 1 for one stripe above
        -1 for one stripe below, etc.). This is useful because linear PDEs can always be 
        represented by stripes in a matrix.

    Methods
    -------
    __str__(self):
        Return string representaion of the dict.
    __add__(self, other):
        Add the entries on each diagonal in the union of both keys (matrix addition).
    __sub__(self, other):
        Sub the entries on each diagonal in the union of both keys (matrix substraction).
    __mul__(self, other):
        Multiply values of the attribute by an int/float.
    __truediv__(self, other):
        Define division by a symbol, will be useful to divide by dx (1st derivative in x), 
        dx**2 (2nd derivative in x), etc.
    __call__(self, val, symb):
        It will be common to have expressions in the values of the attribute. Calling the
        class will evaluate the symbols in the expressions (with names symb)
        at the value specified (val).
    __eq__(self, other):
        Define equality as equality in the values of attributes.
    clean(self):
        Remove all zero values (since these won't affect matrix add/sub)
    max_key(self):
        Return the largest key in the attribute. Useful to find the order in time.
    round_vals(self):
        Round all attribute values for test purposes.
    combine_x_and_t(self, other, method_time):
        Given ExpressionLists for x and t (self and other respectively), return 4
        dicts, the first giving info on how the matrix should be filled, the
        next 2 give info about the rhs terms (because of x and t terms respectively),
        and the last one about the boundary terms. The assumpiton is made that all the
        unknowns are move the the t-side of the equation, accoridngly, the rhs is the
        x-side of the equation.

    See Also
    --------
    Expressions : Can be used as values of the attribute.
    TreeNode: Evaluating the expressions at a certain value in __call__.
    """

    def __init__(self, expr_dict):
        self.expr_dict = expr_dict

    def __str__(self):
        """Return string representation of the attribute."""
        return str(self.expr_dict)

    def __repr__(self):
        """Return string representation of the anme of the class and attribute."""
        return type(self).__name__ + repr(self.expr_dict)

    def __add__(self, other):
        """Define addition between ExpressionLists."""
        if not isinstance(other, ExpressionList):
            raise NotImplementedError(f"Can not add a {type(other)} to an ExpressionList.")
        d1 = self.expr_dict
        d2 = other.expr_dict
        d_added = {k_val: d1.get(k_val, 0) + d2.get(k_val, 0) for k_val in (d1.keys() | d2.keys())}
        return ExpressionList(d_added)

    def __mul__(self, other):
        """Define addition between an ExpressionList and a Number."""
        if not isinstance(other, (int, float)):
            raise NotImplementedError(f"Multiplication only defined for int, float, not {type(other)}.")
        d1 = self.expr_dict
        d_mul = {k: d1.get(k, 0) * other for k in (d1.keys())}
        return ExpressionList(d_mul)

    def __sub__(self, other):
        """Define substraction between ExpressionLists."""
        d1 = self.expr_dict
        d2 = other.expr_dict
        d_sub = {k_val: d1.get(k_val, 0) - d2.get(k_val, 0) for k_val in (d1.keys() | d2.keys())}
        return ExpressionList(d_sub)

    def __truediv__(self, other):
        """Define division of ExpressionList by a Symbol (from Expressions class)."""
        if isinstance(other, Symbol):
            d1 = self.expr_dict
            d_div = {k: d1.get(k, 0) / other for k in (d1.keys())}
            return ExpressionList(d_div)
        else:
            raise NotImplementedError

    def __call__(self, val, symb):
        """Evaluate Expressions inside ExpressionList at a certain value."""
        name = str(symb)
        expr = self.expr_dict
        expr = ExpressionList({k: postvisitor(expr.get(k), evaluate, symbol_map={name: val}) for k in expr.keys()})
        expr.clean()
        return expr

    def __eq__(self, other):
        """Define equality between ExpressionLists."""
        return self.expr_dict == other.expr_dict

    def clean(self, val=0):
        """Remove zero values from attribute."""
        self.expr_dict = {k: v for k, v in self.expr_dict.items() if v != val}

    def max_key(self):
        """Return the largest key from attribute."""
        return max(k for k, v in self.expr_dict.items())

    def round_vals(self):
        """Round values inside attributes."""
        return ExpressionList({k: np.round(v) for k, v in self.expr_dict.items()})

    def combine_x_and_t(self, other, method_time):
        """Transform two ExpressionLists into useful dicts to define matrix/rhs.

        Example:
        -------
        Equation Uxx = 2*Ut is represented by two ExpressionLists as follows
        for implicit, centered scheme for x, and forward scheme for t (dx=dt=1):
        In x: expr_x = ExpressionList({0: -2, 1: 1, -1: 1}) (order does not matter)
        In t: expr_t = ExpressionList({0: -2, 1: 2}) (order does not matter)
        Calling expr_x.combine_x_and_t(expr_t, "imp") will do the following:

        From the ExpressionLists, the equation is: (j for time, i for space)
            U(i+1,j+1) - 2 * U(i,j+1) + U(i-1,j+1) = 2 * U(i,j+1) - 2 * U(i,j)
        This function arranges the equation as such: (unknowns to the lhs)
            2 * U(i,j+1) + 2 * U(i,j+1) - U(i+1,j+1) - U(i-1,j+1) =  2 * U(i,j)
        And it will then retunr:
            mat_dict = {0: 4, 1: -1, -1: -1} (order might change)
            rhs_x = None (all x terms are on the lhs)
            rhs_t = {0: 2} (Since the rhs is evaluated at j (key = 0))
            bc_x = {1: 1, -1: 1} (any term that is not on the diagonal will
                                    contribute for boundary conditions).
        """
        t_dict = other.expr_dict
        k_max = max(k for k in t_dict.keys())
        bc_x = self.expr_dict.copy()
        try:
            bc_x[0]
            del bc_x[0]
        except (KeyError):
            pass
        if method_time == "imp":
            t_max = ExpressionList({0: t_dict.get(k_max)})
            del t_dict[k_max]
            rhs_t = {k: -v for k, v in t_dict.items()}
            mat_dict = (t_max - self).expr_dict
            rhs_x = None
            return mat_dict, rhs_x, rhs_t, bc_x
        elif method_time == "exp":
            mat_dict = {0: t_dict.get(k_max)}
            del t_dict[k_max]
            rhs_t = {k: -v for k, v in t_dict.items()}
            return mat_dict, self.expr_dict, rhs_t, bc_x
        else:
            raise NotImplementedError(f"Only exp and imp methods implemented, not {method_time}")
