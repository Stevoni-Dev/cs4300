# Showing different uses of datatypes


def add_numbers(number1: int, number2: int) -> int | bool:
    if not isinstance(number1, int) or not isinstance(number2, int) or isinstance(number1, bool) or isinstance(number2, bool):
        print("Only provide integers")
        return False
    return number1 + number2

def divide_numbers(number1: int | float, number2: int | float) -> int | float | bool:
    if not isinstance(number1, (int, float)) or not isinstance(number2, (int, float)) or isinstance(number1, bool) or isinstance(number2, bool):
        print("Only provide integers or floats")
        return False
    if number2 == 0:
        print("Cannot divide by zero")
        return False
    return number1 / number2

def string_upper(string: str) -> str | bool:
    if not isinstance(string, str):
        print("Only provide strings")
        return False
    return string.upper()

def is_able_to_drive(age: int) -> bool:
    if not isinstance(age, int) or isinstance(age, bool):
        print("Only provide an integer age")
        return False
    return age >= 16
