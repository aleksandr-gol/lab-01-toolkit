import os
import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "toolkit", *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        timeout=10,
        check=False,
    )


def test_help() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "calc" in result.stdout and "convert" in result.stdout
    assert result.stderr == ""


def test_calc() -> None:
    result = run_cli("calc", "2 + 3 * 4")
    assert result.returncode == 0
    assert float(result.stdout) == 14
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("-7 // 3", -3), ("-5+2", -3), ("-.5 * 2", -1), ("-7 % 3", 2)],
)
def test_negative_expression(expression: str, expected: float) -> None:
    result = run_cli("calc", expression)
    assert result.returncode == 0
    assert float(result.stdout) == pytest.approx(expected)
    assert result.stderr == ""


def test_explicit_separator() -> None:
    result = run_cli("calc", "--", "-7 // 3")
    assert result.returncode == 0
    assert float(result.stdout) == -3
    assert result.stderr == ""


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_calc_help(option: str) -> None:
    result = run_cli("calc", option)
    assert result.returncode == 0
    assert "expression" in result.stdout
    assert result.stderr == ""


def test_convert() -> None:
    result = run_cli("convert", "-273.15", "--from", "c", "--to", "k")
    assert result.returncode == 0
    assert float(result.stdout) == 0
    assert result.stderr == ""


@pytest.mark.parametrize(
    "arguments",
    [
        ("calc", "1/0"),
        ("calc", ""),
        ("calc", "-1/0"),
        ("calc", "-2+"),
        ("calc", "--"),
        ("calc", "2", "3"),
        ("convert", "abc", "--from", "m", "--to", "cm"),
        ("convert", "1", "--from", "m"),
        ("calc",),
        (),
    ],
)
def test_cli_error(arguments: tuple[str, ...]) -> None:
    result = run_cli(*arguments)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr
    assert "Traceback" not in result.stderr
