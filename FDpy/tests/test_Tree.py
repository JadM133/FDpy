
"""Test methods of Expressions and TreeNode."""


import pytest
from FDpy.expressions import Symbol, Number, Add, Sub, Mul, Div, Pow
from FDpy.treenode import evaluate, postvisitor


@pytest.fixture
def test_operands():
    """Defining operands of type Number or Symbol to test the methods on."""
    x = Symbol("x")
    y = Symbol("y")
    n1 = Number(3)
    n2 = Number(0)
    return x, y, n1, n2


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x+y"),
        (2, 1, "3+y"),
        (2, 3, "3"),
    ],
)
def test_add(idx1, idx2, str_val, test_operands):
    """Test the addition of two expressions."""
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Add((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Add((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x-y"),
        (2, 1, "3-y"),
        (2, 3, "3"),
    ],
)
def test_sub(idx1, idx2, str_val, test_operands):
    """Test the substraction of two expressions."""
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Sub((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Sub((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x*y"),
        (2, 1, "3*y"),
        (2, 3, "0"),
    ],
)
def test_mul(idx1, idx2, str_val, test_operands):
    """Test the multiplication of two expressions."""
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Mul((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Mul((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x/y"),
        (2, 1, "3/y"),
    ],
)
def test_div(idx1, idx2, str_val, test_operands):
    """Test the division of two expressions."""
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Div((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Div((x, y)))}"


def test_div_error():
    """Test if division by zero leads to an error."""
    d1 = Number(3)
    d2 = Number(0)
    with pytest.raises(ZeroDivisionError):
        d1 / d2
    with pytest.raises(ZeroDivisionError):
        d1 / 0


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x^y"),
        (2, 1, "3^y"),
        (2, 3, "3^0"),
    ],
)
def test_pow(idx1, idx2, str_val, test_operands):
    """Test the power of two expressions."""
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Pow((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Pow((x, y)))}"


@pytest.fixture
def test_expr_eval():
    """Define expressions to test evaluation on."""
    x = Symbol("x")
    y = Symbol("y")
    test_vals = [
        (1 / x + 2 - y, 4, 2, 0.25),
        (x / y + 2 * x - y + 1, 8, 2, 19),
        (x * x + 2 * y - y * 5, 2, 3, -5),
        (x * (2 + y) - (y + x) * (x + 2 * y), 1, 2, -11),
        (x**y + y**2 + 2 * (x + y) ** 5, 1, 2, 491),
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0), (1), (2), (3), (4)])
def test_evaluation(test_expr_eval, idx):
    """Test of expressions are evaluated the right way."""
    expr, x, y, result = test_expr_eval[idx]
    computed_res = postvisitor(expr, evaluate, symbol_map={"x": x, "y": y})
    assert computed_res == result, f"expected an evaluation of {result} for expression {expr}, got {computed_res}"


@pytest.fixture
def test_expr_print():
    """Define expressions to test their display."""
    x = Symbol("x")
    y = Symbol("y")
    two = Number(2)
    four = Number(4)
    test_vals = [
        ((2 + x) * 3 - 2 / (5 + y), "(2+x)*3-2/(5+y)"),
        ((1 / x) / ((y - (x))), "1/x/(y-x)"),
        (y + 2 + (5 * x) - (2 + 5 * (x + 2)), "y+2+5*x-(2+5*(x+2))"),
        ((2 + x * 5) * (two * four) * (2 + y), "(2+x*5)*2*4*(2+y)"),
        (
            x ** (y + 2) + 2 ** (x / y) / (2**x + y),
            "x^(y+2)+2^(x/y)/(2^x+y)",
        ),
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0), (1), (2), (3), (4)])
def test_display(test_expr_print, idx):
    """Test if expressions are being displayed as expected."""
    expr, result = test_expr_print[idx]
    print(str(expr))
    assert str(expr) == result, f"expected an evaluation of {result} for expression {expr}"
