"""Разбор и вычисление выражений без скобок."""

from math import isfinite

from toolkit.errors import ToolkitError

OPERATORS = {"+", "-", "*", "/", "//", "%"}
DIGITS = "0123456789"


# Разбиваем строку на числа и знаки операций. Пока всё хранится в виде строк.
def tokenize(expression: str) -> list[str]:
    tokens = []
    position = 0
    while position < len(expression):
        char = expression[position]
        if char.isspace():
            position += 1
        elif char in DIGITS + ".":
            start = position
            while position < len(expression) and expression[position] in DIGITS + ".":
                position += 1
            tokens.append(expression[start:position])
        elif expression[position : position + 2] == "//":
            tokens.append("//")
            position += 2
        elif char in OPERATORS:
            tokens.append(char)
            position += 1
        else:
            raise ToolkitError(f"Недопустимый символ: {char}")
    return tokens


# Проверяем порядок чисел и операций. Плюс или минус перед числом учитываем как знак.
def validate(tokens: list[str]) -> tuple[list[float], list[str]]:
    if not tokens:
        raise ToolkitError("Пустое выражение.")
    numbers = []
    operators = []
    position = 0
    while position < len(tokens):
        sign = 1
        if tokens[position] in {"+", "-"}:
            if tokens[position] == "-":
                sign = -1
            position += 1
        if position == len(tokens) or tokens[position] in OPERATORS:
            raise ToolkitError("Пропущен операнд или указаны лишние операторы.")
        try:
            number = float(tokens[position]) * sign
        except ValueError as error:
            raise ToolkitError(f"Неверное число: {tokens[position]}") from error
        if not isfinite(number):
            raise ToolkitError("Число слишком большое.")
        numbers.append(number)
        position += 1
        if position < len(tokens):
            if tokens[position] not in OPERATORS:
                raise ToolkitError("Между числами пропущен оператор.")
            operators.append(tokens[position])
            position += 1
            if position == len(tokens):
                raise ToolkitError("После оператора пропущен операнд.")
    return numbers, operators


# Выполняем одну операцию с двумя числами и проверяем результат.
def apply_operation(left: float, operator: str, right: float) -> float:
    if operator in {"/", "//", "%"} and right == 0:
        raise ToolkitError("Деление на ноль.")
    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        result = left / right
    elif operator == "//":
        result = left // right
    elif operator == "%":
        result = left % right
    else:
        raise ToolkitError(f"Неизвестный оператор: {operator}")
    if not isfinite(result):
        raise ToolkitError("Результат слишком большой.")
    return result


# Сначала считаем умножение, деление и остаток, затем сложение и вычитание.
def calculate(numbers: list[float], operators: list[str]) -> float:
    reduced_numbers = []
    reduced_operators = []
    current = numbers[0]
    for operator, number in zip(operators, numbers[1:]):
        if operator in {"*", "/", "//", "%"}:
            current = apply_operation(current, operator, number)
        else:
            reduced_numbers.append(current)
            reduced_operators.append(operator)
            current = number
    reduced_numbers.append(current)

    result = reduced_numbers[0]
    for operator, number in zip(reduced_operators, reduced_numbers[1:]):
        result = apply_operation(result, operator, number)
    return result


# По очереди разбираем строку, проверяем её и считаем ответ.
def evaluate(expression: str) -> float:
    tokens = tokenize(expression)
    numbers, operators = validate(tokens)
    return calculate(numbers, operators)
