class Expressions:
    def __init__(self, operands: tuple):
        self.operands = operands

    def __add__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Add((self, other))

    def __radd__(self, other):
        other = Number(other)
        return Add((other, self))

    def __mul__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Mul((self, other))

    def __rmul__(self, other):
        other = Number(other)
        return Mul((other, self))

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

    def __pow__(self, other):
        other = Number(other) if type(other) == (int or float) else other
        return Pow((self, other))

    def __rpow__(self, other):
        other = Number(other)
        return Pow((other, self))


class Operator(Expressions):
    def __repr__(self):
        return type(self).__name__ + repr(self.operands)

    def str_old(self):
        str_val = []
        str_val += [str_val.value for str_val in self.operands]
        return str_val

    def __str__(self):
        if isinstance(self.operands, (int, float, Number, Symbol)):
            str_val = str(self.operands) + self.symbol
            return str_val
        else:
            str_operand1 = str(self.operands[0])

            if self.precedence > self.operands[0].precedence:
                str_operand1 = f"({str_operand1})"

            if len(self.operands) == 2:
                str_operand2 = str(self.operands[1])

                if self.precedence == self.operands[1].precedence and type(self) == Sub:
                    str_operand2 = f"({str_operand2})"

                if self.precedence > self.operands[1].precedence:
                    str_operand2 = f"({str_operand2})"

                str_both = self.symbol.join((str_operand1, str_operand2))
            else:
                str_both = str_operand1 + self.symbol

            return str_both


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


class Pow(Operator):
    def __init__(self, operands: tuple):
        super().__init__(operands)
        self.symbol = " ^ "
        self.precedence = 3


class F(Operator):
    def __init__(self, other):
        super().__init__(other)
        if isinstance(self.operands, (int, float)):
            self.operands = Number(self.operands)
        self.symbol = "!"
        self.precedence = 4


class Terminal(Expressions):
    def __init__(self, operands: tuple, value):
        super().__init__(operands)
        self.value = value
        self.precedence = 5

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __iter__(self):
        return TerminalIterator(self)


class Symbol(Terminal):
    def __init__(self, value, operands=[]):
        super().__init__(operands, value)


class Number(Terminal):
    def __init__(self, value, operands=[]):
        super().__init__(operands, value)


class TerminalIterator:
    def __init__(self, operands):
        self.operands = operands
        self.stop = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.stop == 1:
            raise StopIteration
        self.stop = 1
        return self.operands
