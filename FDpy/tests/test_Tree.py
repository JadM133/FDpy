import pytest
from expressions import Symbol, Number, Add, Sub, Mul, Div, Pow, F
from treenode import evaluate, postvisitor


@pytest.fixture
def test_operands():
    x = Symbol("x")
    y = Symbol("y")
    n1 = Number(3)
    n2 = Number(0)
    return x, y, n1, n2


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x + y"),
        (2, 1, "3 + y"),
        (2, 3, "3 + 0"),
    ],
)
def test_add(idx1, idx2, str_val, test_operands):
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Add((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Add((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x - y"),
        (2, 1, "3 - y"),
        (2, 3, "3 - 0"),
    ],
)
def test_sub(idx1, idx2, str_val, test_operands):
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Sub((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Sub((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x * y"),
        (2, 1, "3 * y"),
        (2, 3, "3 * 0"),
    ],
)
def test_mul(idx1, idx2, str_val, test_operands):
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Mul((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Mul((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x / y"),
        (2, 1, "3 / y"),
        (2, 3, "3 / 0"),
    ],
)
def test_div(idx1, idx2, str_val, test_operands):
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Div((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Div((x, y)))}"


@pytest.mark.parametrize(
    "idx1, idx2, str_val",
    [
        (0, 1, "x ^ y"),
        (2, 1, "3 ^ y"),
        (2, 3, "3 ^ 0"),
    ],
)
def test_pow(idx1, idx2, str_val, test_operands):
    x, y = test_operands[idx1], test_operands[idx2]
    assert (
        str(Pow((x, y))) == str_val
    ), f"expected string representation of {str_val} \
     but got {str(Pow((x, y)))}"


@pytest.fixture
def test_expr_eval():
    x = Symbol("x")
    y = Symbol("y")
    test_vals = [
        (1 / x + 2 - y, 4, 2, 0.25),
        (x / y + 2 * x - y + 1, 8, 2, 19),
        (x * x + 2 * y - y * 5, 2, 3, -5),
        (x * (2 + y) - (y + x) * (x + 2 * y), 1, 2, -11),
        (x**y + y**2 + 2 * (x + y) ** 5, 1, 2, 491),
        ((y + F(2) ** 2) + 6 / F(x), 3, 2, 7),
        (x / F(y), 1, 3, 0.1666666666666666666),
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0), (1), (2), (3), (4), (5), (6)])
def test_evaluation(test_expr_eval, idx):
    expr, x, y, result = test_expr_eval[idx]
    computed_res = postvisitor(expr, evaluate, symbol_map={"x": x, "y": y})
    assert (
        computed_res == result
    ), f"expected an evaluation of {result} for expression {expr}, got {computed_res}"


@pytest.fixture
def test_expr_print():
    x = Symbol("x")
    y = Symbol("y")
    two = Number(2)
    four = Number(4)
    test_vals = [
        ((2 + x) * 3 - 2 / (5 + y), "(2 + x) * 3 - 2 / (5 + y)"),
        ((1 / x) / ((y - (x))), "1 / x / (y - x)"),
        (y + 2 + (5 * x) - (2 + 5 * (x + 2)), "y + 2 + 5 * x - (2 + 5 * (x + 2))"),
        ((2 + x * 5) * (two * four) * (2 + y), "(2 + x * 5) * 2 * 4 * (2 + y)"),
        (
            x ** (y + 2) + 2 ** (x / y) / (2**x + y),
            "x ^ (y + 2) + 2 ^ (x / y) / (2 ^ x + y)",
        ),
        ((2 + F(4) ** 3) ** 4 / F(x), "(2 + 4! ^ 3) ^ 4 / x!"),
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0), (1), (2), (3), (4), (5)])
def test_display(test_expr_print, idx):
    expr, result = test_expr_print[idx]
    print(str(expr))
    assert (
        str(expr) == result
    ), f"expected an evaluation of {result} for expression {expr}"


@pytest.fixture
def test_expr_simp():
    x = Symbol("x")
    y = Symbol("y")
    two = Number(2)
    four = Number(4)
    test_vals = [
        ((2+x)/y**x, 5, Symbol('y'), "7 / y ^ 5")
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0)])
def test_simp(test_expr_simp, idx):
    expr, x, y, result = test_expr_simp[idx]
    pred = postvisitor(expr, evaluate, symbol_map={"x": x, "y": y})
    print(type(pred))
    assert (
        str(pred) == result
    ), f"expected an evaluation of {result} for expression {expr}, got {pred}"
