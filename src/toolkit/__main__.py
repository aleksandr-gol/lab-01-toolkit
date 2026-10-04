"""Аргументы командной строки и вывод результатов."""

import argparse
import sys

from toolkit.calculator import evaluate
from toolkit.converter import convert
from toolkit.errors import ToolkitError


# Читаем команду и запускаем нужную функцию. Возвращаем 0 при успехе, 2 при ошибке.
def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m toolkit", description="Калькулятор и конвертер величин"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    calculator = commands.add_parser("calc", help="Вычислить выражение")
    calculator.add_argument("expression", help="Выражение в кавычках, без скобок")
    converter = commands.add_parser("convert", help="Перевести величину")
    converter.add_argument("value", help="Числовое значение")
    converter.add_argument("--from", dest="from_unit", required=True, help="Исходная единица")
    converter.add_argument("--to", dest="to_unit", required=True, help="Нужная единица")
    if arguments is None:
        arguments = sys.argv[1:]
    if len(arguments) == 2 and arguments[0] == "calc":
        if arguments[1] not in {"-h", "--help", "--"}:
            arguments = ["calc", "--", arguments[1]]
    args = parser.parse_args(arguments)
    try:
        if args.command == "calc":
            result = evaluate(args.expression)
        else:
            result = convert(args.value, args.from_unit, args.to_unit)
    except ToolkitError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
