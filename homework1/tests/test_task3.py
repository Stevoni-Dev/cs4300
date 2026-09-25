import pytest
from src.task3 import signum, is_prime, first_ten_prime, triangle_of_100

signum_valid_positive_values = [*range(1,20), 0.1, 4.5, 15.5]
signum_valid_negative_values = [*range(-20, -1), -0.9, -11.1]
signum_valud_zero_values = [0.0, 0]
signum_invalid_inputs = [True, False, "Orange", [1, 2, 3], {"a": 1}, None]

@pytest.mark.parametrize("valid_positive_value", signum_valid_positive_values)
def test_signum_positive(capsys, valid_positive_value):
    signum(valid_positive_value)
    captured = capsys.readouterr()
    assert captured.out == "Number is positive\n"

@pytest.mark.parametrize("valid_negative_value", signum_valid_negative_values)
def test_signum_negative(capsys, valid_negative_value):
    signum(valid_negative_value)
    captured = capsys.readouterr()
    assert captured.out == "Number is negative\n"

@pytest.mark.parametrize("valid_zero_value", signum_valud_zero_values)
def test_signum_zero(capsys, valid_zero_value):
    signum(valid_zero_value)
    captured = capsys.readouterr()
    assert captured.out == "Number is zero\n"

@pytest.mark.parametrize("invalid_value", signum_invalid_inputs)
def test_signum_incorrect_input(capsys, invalid_value):
    with pytest.raises(TypeError):
        signum(invalid_value)
        captured = capsys.readouterr()
        assert captured.out == "Must provide integer or floating number\n"

prime_numbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
non_prime_numbers = [item for item in range(0,31) if item not in prime_numbers]
non_prime_numbers.extend(range(-20, -1))
is_prime_invalid_inputs = [True, False, "Orange", [1, 2, 3], {"a": 1}, None, 3.14]

print(non_prime_numbers)

@pytest.mark.parametrize("prime_number", prime_numbers)
def test_is_prime_with_prime_number(prime_number):
    assert is_prime(prime_number) == True

@pytest.mark.parametrize("non_prime_number", non_prime_numbers)
def test_is_prime_with_non_prime_number(non_prime_number):
    assert is_prime(non_prime_number) == False

@pytest.mark.parametrize("invalid_input", is_prime_invalid_inputs)
def test_is_prime_with_invalid_input(capsys, invalid_input):
    with pytest.raises(TypeError):
        is_prime(invalid_input)
        captured = capsys.readouterr()
        assert captured.out == "Must provide natural number\n"

def test_first_ten_prime(capsys):
    first_ten_prime()
    captured = capsys.readouterr()
    assert captured.out == "2\n3\n5\n7\n11\n13\n17\n19\n23\n29\n"

def test_triangle_of_100():
    assert triangle_of_100() == 5050