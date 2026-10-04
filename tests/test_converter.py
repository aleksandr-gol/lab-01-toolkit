import json
from pathlib import Path

import pytest

from toolkit import converter
from toolkit.converter import convert
from toolkit.errors import ToolkitError


@pytest.mark.parametrize(
    ("value", "source", "target", "expected"),
    [
        (1, "km", "m", 1000),
        (1000, "mm", "m", 1),
        (100, "cm", "m", 1),
        (1, "kg", "g", 1000),
        (500, "g", "kg", 0.5),
        (1, "M", "CM", 100),
        (0, "c", "f", 32),
        (212, "f", "c", 100),
        (0, "c", "k", 273.15),
        (273.15, "k", "c", 0),
        (-273.15, "c", "k", 0),
        (-459.67, "f", "k", 0),
        (0, "k", "f", -459.67),
        (23, "c", "c", 23),
        (2, "m", "m", 2),
    ],
)
def test_convert(value: float, source: str, target: str, expected: float) -> None:
    result = convert(value, source, target)
    assert isinstance(result, float)
    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("value", "source", "target"),
    [
        (1, "unknown", "m"),
        (1, "m", "unknown"),
        (1, "m", "kg"),
        (-273.16, "c", "k"),
        (-459.68, "f", "c"),
        (-0.01, "k", "k"),
        ("abc", "m", "cm"),
        ("", "m", "cm"),
        ("nan", "m", "cm"),
        ("inf", "m", "cm"),
        ("1e309", "m", "cm"),
        ("1e308", "km", "mm"),
    ],
)
def test_invalid_conversion(value: str | float, source: str, target: str) -> None:
    with pytest.raises(ToolkitError):
        convert(value, source, target)


def test_table_loaded_from_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = tmp_path / "units.json"
    config.write_text(json.dumps({"length": {"m": 1, "custom": 2}}), encoding="utf-8")
    monkeypatch.setattr(converter, "CONFIG_PATH", config)
    assert convert(3, "custom", "m") == 6.0


def test_missing_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(converter, "CONFIG_PATH", tmp_path / "missing.json")
    with pytest.raises(ToolkitError, match="таблицу"):
        convert(1, "m", "cm")
