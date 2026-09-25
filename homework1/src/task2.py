# Showing different uses of datatypes


def add_numbers(number1: int, number2: int) -> int | bool:
    if not isinstance(number1, int) or not isinstance(number2, int) or isinstance(number1, bool) or isinstance(number2, bool):
        raise TypeError("Only provide integers")
    return number1 + number2

def divide_numbers(number1: int | float, number2: int | float) -> int | float | bool:
    if not isinstance(number1, (int, float)) or not isinstance(number2, (int, float)) or isinstance(number1, bool) or isinstance(number2, bool):
        raise TypeError("Only provide integers or floats")
    if number2 == 0:
        raise TypeError("Cannot divide by zero")
    return number1 / number2

def string_upper(string: str) -> str | bool:
    if not isinstance(string, str):
        raise TypeError("Only provide strings")
    return string.upper()

def is_able_to_drive(age: int) -> bool:
    if not isinstance(age, int) or isinstance(age, bool):
        raise TypeError("Only provide an integer age")
    return age >= 16
