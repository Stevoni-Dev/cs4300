import pytest
from src.task2 import add_numbers, divide_numbers, string_upper, is_able_to_drive

@pytest.mark.parametrize(
    "num1, num2, answer", 
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (-5, -3, -8),
        (10, -4, 6),
        (100, 200, 300),
        (1000000, 2000000, 3000000),
    ],
)
def test_add_numbers_valid_inputs(num1, num2, answer):
    assert add_numbers(num1, num2) == answer


@pytest.mark.parametrize(
    "num1, num2",
    [
    (1.5, 2),
    (1, 2.5),
    ("1", 2),
    (1, "2"),
    ("1", "2"),
    (None, 2),
    (1, None),
    (True, 2),
    (1, False),
    ([], 2),
    (1, []),
    ({}, 2),
    (1, {}),
]
)
def test_add_numbers_invalid_input(capsys, num1, num2):
    with pytest.raises(TypeError):
        result = add_numbers(num1, num2)
        captured = capsys.readouterr()
        assert captured.out == "Only provide integers\n"
        assert result == False

@pytest.mark.parametrize(
    "number1, number2, answer",
    [
        (10, 2, 5),
        (10, 5, 2),
        (9, 3, 3),
        (7, 2, 3.5),
        (5.0, 2, 2.5),
        (10, 4.0, 2.5),
        (5.5, 2.0, 2.75),
        (-10, 2, -5),
        (10, -2, -5),
        (-10, -2, 5),
        (0, 5, 0),
        (1, 2, 0.5),
        (1000000, 100, 10000),
    ],
)
def test_divide_numbers_valid_inputs(number1, number2, answer):

    assert divide_numbers(number1, number2) == answer

@pytest.mark.parametrize(
    "number1, number2",
    [
        ("10", 2),
        (10, "2"),
        (None, 2),
        (10, None),
        ([], 2),
        (10, []),
        ({}, 2),
        (10, {}),
        (True, 2),
        (10, False),
    ],
)
def test_divide_numbers_invalid_types(capsys, number1, number2):
    with pytest.raises(TypeError):
        result = divide_numbers(number1, number2)
        captured = capsys.readouterr()

        assert captured.out == "Only provide integers or floats\n"
        assert result == False

@pytest.mark.parametrize(
    "number1, number2",
    [
        (10, 0),
        (0, 0),
        (-10, 0),
        (10.5, 0),
        (10, 0.0),
        (10.5, 0.0),
        (-10.5, 0.0),
    ],
)
def test_divide_numbers_zero_divisor(capsys, number1, number2):
    with pytest.raises(TypeError):
        result = divide_numbers(number1, number2)
        captured = capsys.readouterr()

        assert captured.out == "Cannot divide by zero\n"
        assert result == False

@pytest.mark.parametrize(
    "string, answer",
    [
        ("hello", "HELLO"),
        ("Hello", "HELLO"),
        ("HELLO", "HELLO"),
        ("hello world", "HELLO WORLD"),
        ("Python is fun", "PYTHON IS FUN"),
        ("123abc", "123ABC"),
        ("hello123", "HELLO123"),
        ("hello-world", "HELLO-WORLD"),
        ("", ""),
        ("a", "A"),
    ],
)
def test_string_upper_valid_inputs(string, answer):

    assert string_upper(string) == answer


@pytest.mark.parametrize(
    "string",
    [
        123,
        1.5,
        True,
        False,
        None,
        [],
        [1, 2, 3],
        {},
        {"key": "value"},
        (1, 2, 3),
    ],
)
def test_string_upper_invalid_input(capsys, string):
    with pytest.raises(TypeError):
        result = string_upper(string)
        captured = capsys.readouterr()

        assert captured.out == "Only provide strings\n"
        assert result == False

@pytest.mark.parametrize(
    "age, answer",
    [
        (16, True),
        (17, True),
        (18, True),
        (21, True),
        (25, True),
        (50, True),
        (100, True),
        (15, False),
        (10, False),
        (5, False),
        (0, False),
    ],
)
def test_is_able_to_drive_valid_inputs(age, answer):
    assert is_able_to_drive(age) == answer


@pytest.mark.parametrize(
    "age",
    [
        16.5,
        15.5,
        "16",
        "fifteen",
        None,
        [],
        [16],
        {},
        {"age": 16},
        (16,),
        True,
        False,
    ],
)
def test_is_able_to_drive_invalid_input(capsys, age):
    with pytest.raises(TypeError):
        result = is_able_to_drive(age)
        captured = capsys.readouterr()
        assert captured.error == "Only provide an integer age\n"
        assert result == False