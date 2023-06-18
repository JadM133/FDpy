class Expressions:
    def __init__(self, operands: tuple):
        self.operands = operands

    def __add__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Add((self, other))

    def __radd__(self, other):
        other = Number(other)
        return Add((self, other))

    def __mul__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Mul((self, other))

    def __rmul__(self, other):
        other = Number(other)
        return Mul((self, other))

    def __truediv__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Div((self, other))

    def __rtruediv__(self, other):
        other = Number(other)
        return Div((other, self))

    def __sub__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Sub((self, other))

    def __rsub__(self, other):
        other = Number(other)
        return Sub((other, self))


class Operator(Expressions):
    def __repr__(self):
        return type(self).__name__ + repr(self.operands)

    def str_old(self):
        str_val = []
        str_val += [str_val.value for str_val in self.operands]
        return str_val

    def __str__(self, oper_type=None):
        str_val = self.symbol.join(
            (
                self.operands[0].__str__(self),
                self.operands[1].__str__(self),
            )
        )
        if oper_type is not None and self.precedence < oper_type.precedence:
            return "(" + str_val + ")"
        else:
            return str_val


class Add(Operator):
    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = " + "
        self.precedence = 1


class Sub(Operator):
    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = " - "
        self.precedence = 1


class Mul(Operator):
    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = " * "
        self.precedence = 2


class Div(Operator):
    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = " / "
        self.precedence = 2


class Terminal(Expressions):
    def __init__(self, operands: tuple, value):
        super().__init__(operands)
        self.value = value
        self.precedence = 0

    def __str__(self, operand_type):
        return str(self.value)

    def __repr__(self, operand_type):
        return repr(self.value)


class Symbol(Terminal):
    def __init__(self, value, operands=[]):
        super().__init__(operands, value)


class Number(Terminal):
    def __init__(self, value, operands=[]):
        super().__init__(operands, value)
