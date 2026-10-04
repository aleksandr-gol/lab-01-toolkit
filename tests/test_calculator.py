import pytest

from toolkit.calculator import evaluate, tokenize
from toolkit.errors import ToolkitError


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2+2", 4),
        ("7 + 8 / 4 - 1", 8),
        ("10 / 4 + 2", 4.5),
        ("-5 + 2 * -3", -11),
        ("+5", 5),
        ("2 - -3", 5),
        ("2 + +3", 5),
        ("20 / 2 * 3", 30),
        ("10 - 3 - 2", 5),
        (" .5 + 2. ", 2.5),
        ("2\t+\n3", 5),
        ("-7 // 3", -3),
        ("7 // -3", -3),
        ("-7 % 3", 2),
        ("7 % -3", -2),
        ("-7.5 // 2", -4),
        ("-7.5 % 2", 0.5),
        ("2 + 9 // 2 * 3 % 5", 4),
    ],
)
def test_evaluate(expression: str, expected: float) -> None:
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "2+a",
        "2+",
        "*2",
        "2*/3",
        "2**3",
        "2 3",
        "1..2",
        ".",
        "1/0",
        "1//0",
        "1%0",
        "1/-0",
        "--2",
        "(2+3)",
        "2,5",
        "9" * 400,
    ],
)
def test_invalid_expression(expression: str) -> None:
    with pytest.raises(ToolkitError):
        evaluate(expression)


def test_tokenize_keeps_sign_separate() -> None:
    assert tokenize("2 + 3.5 * -4") == ["2", "+", "3.5", "*", "-", "4"]


def test_overflow() -> None:
    with pytest.raises(ToolkitError, match="слишком большой"):
        evaluate("9" * 200 + " * " + "9" * 200)
