
"""Defines Expressions class and all its subclasses and their iterators."""


class Expressions:
    """A class to represent a symbolic expression.

    Parameters
    ----------
    operands: tuple
        Two for operators, and one for terminal nodes.

    Methods
    -------
    Check the docstrings within the methods for more details.

    See Also
    --------
    class TreeNode : Create and evaluate trees of expressions.
    """

    def __init__(self, operands: tuple):
        self.operands = operands

    def __add__(self, other):
        """Define the sum of two expressions."""
        other = Number(other) if type(other) == (int or float) else other
        return Add((self, other))

    def __radd__(self, other):
        """Define the reversed sum of two expressions."""
        other = Number(other)
        return Add((other, self))

    def __mul__(self, other):
        """Define the multiplication of two expressions."""
        other = Number(other) if type(other) == (int or float) else other
        return Mul((self, other))

    def __rmul__(self, other):
        """Define the reversed multiplication of two expressions."""
        other = Number(other)
        return Mul((other, self))

    def __truediv__(self, other):
        """Define the division of two expressions."""
        other = Number(other) if type(other) == (int or float) else other
        return Div((self, other))

    def __rtruediv__(self, other):
        """Define the reversed division of two expressions."""
        other = Number(other)
        return Div((other, self))

    def __sub__(self, other):
        """Define the substraction of two expressions."""
        other = Number(other) if type(other) == (int or float) else other
        return Sub((self, other))

    def __rsub__(self, other):
        """Define the reversed substraction of two expressions."""
        other = Number(other)
        return Sub((other, self))

    def __pow__(self, other):
        """Define the one expression to the power of another one."""
        other = Number(other) if type(other) == (int or float) else other
        return Pow((self, other))

    def __rpow__(self, other):
        """Define the reversed power operation."""
        other = Number(other)
        return Pow((other, self))


class Operator(Expressions):
    """Subclass to represent Operators.

    Parameters
    ----------
    operands: tuple
        Two of them in this case (e.g. Add((0, x))))

    Methods
    -------
    __str__(self):
        Return string representaion of the equation.
    """

    def __repr__(self):
        """Represent as string for debugging and other purposes."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """Represent as string for printing.

        This method is quite long and at first glance might look crowded.
        What it is in fact doing is assuring that an equation is represented
        properly (for example 1*x should be written as x, 0+x as x, etc.)
        """
        str_operand1 = str(self.operands[0])

        # Adding parenthesis when needed
        if self.precedence > self.operands[0].precedence:
            str_operand1 = f"({str_operand1})"

        str_operand2 = str(self.operands[1])

        if self.precedence == self.operands[1].precedence and type(self) == Sub:
            str_operand2 = f"({str_operand2})"

        if self.precedence > self.operands[1].precedence:
            str_operand2 = f"({str_operand2})"

        # Taking care of adding or substracting zero
        if (self.operands[0] == 0 or self.operands[1] == 0) and self.precedence == 1:
            if self.operands[0] == 0:
                str_both = str(self.operands[1])
            else:
                str_both = str(self.operands[0])

        # Taking care of multiplying or dividing by zero
        elif (self.operands[0] == 0 or self.operands[1] == 0) and self.precedence == 2:
            if self.operands[0] == 0:
                str_both = "0"
            else:
                if type(self) == Mul:
                    str_both = "0"
                else:
                    raise ZeroDivisionError

        # Making multiplying by one look better!
        elif self.operands[0] == 1 and type(self) == Mul:
            str_both = str(self.operands[1])

        # Fixing the way we add a multiplication with a negative operand
        # i.e. from 1+-2*x to 1-2*x
        elif type(self) == Add and type(self.operands[1]) == Mul:
            dummy = self.operands[1]
            if isinstance(dummy.operands[0], Number) and dummy.operands[0].value < 0:
                str_both = str(self.operands[0]) + str(self.operands[1])
                return str_both
            elif isinstance(dummy.operands[0], (int, float)) and dummy.operands[0] < 0:
                str_both = str(self.operands[0]) + str(self.operands[1])
                return str_both
            else:
                str_both = self.symbol.join(filter(None, (str_operand1, str_operand2)))
        elif (str(self.operands[0]) == "0" or str(self.operands[1]) == "0") and self.precedence == 1:
            str_both = str(self.operands[0]) if str(self.operands[0]) != "0" else str(self.operands[1])
        else:
            str_both = self.symbol.join(filter(None, (str_operand1, str_operand2)))
        return str_both


class Add(Operator):
    """Subclass to add two operands."""

    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = "+"
        self.precedence = 1


class Sub(Operator):
    """Subclass to substract two operands."""

    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = "-"
        self.precedence = 1


class Mul(Operator):
    """Subclass to multiply two operands."""

    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = "*"
        self.precedence = 2


class Div(Operator):
    """Subclass to divide two operands."""

    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = "/"
        self.precedence = 2
        if self.operands[1] == 0:
            raise ZeroDivisionError


class Pow(Operator):
    """Subclass to use power on operands."""

    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = "^"
        self.precedence = 3


class Terminal(Expressions):
    """Subclass to represent Operators.

    Parameters
    ----------
    operands: tuple
        Empty in this case
    value: str/int
        Depending if it is a symbol or a number
    """

    def __init__(self, operands: tuple, value):
        super().__init__(operands)
        self.value = value
        self.precedence = 5

    def __str__(self):
        """Represent symbols/numbers when printing."""
        return str(self.value)

    def __repr__(self):
        """Represent symbols/numbers in debugging/other purposes."""
        return repr(self.value)

    def __iter__(self):
        """Iterate over operands in case nothing was provided as operands."""
        return TerminalIterator(self)

    def __eq__(self, other):
        """Equate two values of two instances of the subclass."""
        if not isinstance(other, Number):
            return self.value == other
        else:
            return self.value == other.value


class Symbol(Terminal):
    """Subclass representing symbols."""

    def __init__(self, value, operands=[]):
        super().__init__(operands, value)


class Number(Terminal):
    """Subclass representing numbers."""

    def __init__(self, value, operands=[]):
        super().__init__(operands, value)


class TerminalIterator:
    """Class to iterate over terminal values.

    Note: The code could have been written without this class. However,
    since we are not forced to provide an empty list of operands, this
    class will avoid running into any errors where we try to iterate
    over either a number or a string.
    """

    def __init__(self, operands):
        self.operands = operands
        self.stop = 0

    def __iter__(self):
        """Return the iterator."""
        return self

    def __next__(self):
        """Define how the iterator advances."""
        if self.stop == 1:
            raise StopIteration
        self.stop = 1
        return self.operands
