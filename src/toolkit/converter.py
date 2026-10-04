"""Конвертация с таблицей коэффициентов в units.json."""

import json
from math import isfinite
from pathlib import Path

from toolkit.errors import ToolkitError

CONFIG_PATH = Path(__file__).with_name("units.json")


# Переводим величину через базовую единицу: метры, килограммы или кельвины.
def convert(value: str | float, from_unit: str, to_unit: str) -> float:
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ToolkitError("Неверное числовое значение.") from error
    if not isfinite(number):
        raise ToolkitError("Значение должно быть конечным числом.")
    try:
        with CONFIG_PATH.open(encoding="utf-8") as file:
            groups = json.load(file)
    except (OSError, ValueError) as error:
        raise ToolkitError("Не удалось прочитать таблицу units.json.") from error

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    source_group = None
    target_group = None
    for group, units in groups.items():
        if from_unit in units:
            source_group = group
        if to_unit in units:
            target_group = group
    if source_group is None or target_group is None:
        raise ToolkitError("Неизвестная единица измерения.")
    if source_group != target_group:
        raise ToolkitError("Нельзя переводить величины из разных групп.")

    units = groups[source_group]
    if source_group == "temperature":
        source = units[from_unit]
        target = units[to_unit]
        if number < source["minimum"]:
            raise ToolkitError("Температура ниже абсолютного нуля.")
        kelvin = (number - source["minimum"]) * source["scale"]
        result = kelvin / target["scale"] + target["minimum"]
    else:
        result = number * units[from_unit] / units[to_unit]
    if not isfinite(result):
        raise ToolkitError("Результат слишком большой.")
    return float(result)
