import pytest
from expressions import Symbol, Number, Add, Sub, Mul, Div
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


@pytest.fixture
def test_expr_eval():
    x = Symbol("x")
    y = Symbol("y")
    test_vals = [
        (1 / x + 2 - y, 4, 2, 0.25),
        (x / y + 2 * x - y + 1, 8, 2, 19),
        (x * x + 2 * y - y * 5, 2, 3, -5),
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0), (1), (2)])
def test_evaluation(test_expr_eval, idx):
    expr, x, y, result = test_expr_eval[idx]
    assert (
        postvisitor(expr, evaluate, symbol_map={"x": x, "y": y}) == result
    ), f"expected an evaluation of {result} for expression {expr}"


@pytest.fixture
def test_expr_print():
    x = Symbol("x")
    y = Symbol("y")
    test_vals = [
        ((2 + x) * 3 - 2 / (5 + y), "(2 + x) * 3 - 2 / (5 + y)"),
        ((1 / x) / ((y - (x))), "1 / x / (y - x)"),
    ]
    return test_vals


@pytest.mark.parametrize("idx", [(0), (1), (2)])
def test_display(test_expr_print, idx):
    expr, result = test_expr_print[idx]
    assert (
        str(expr) == result
    ), f"expected an evaluation of {result} for expression {expr}"
