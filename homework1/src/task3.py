from math import sqrt

# Check for negative, positive, or zero value of number
def signum(number: int | float) -> str:
    if not (isinstance(number, int) or isinstance(number, float)) or isinstance(number, bool):
        raise TypeError("Must provide integer or floating number")
    if number < 0:
        print("Number is negative")
    elif number > 0: 
        print("Number is positive")
    else:
        print("Number is zero")

# Checks if a number is prime
def is_prime(number: int) -> bool:
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("Must provide natural number")
    # Based on algorithm, 1, 0 will flag as prime but it is not
    if number == 1 or number <= 0:
        return False
        
    # Get square root
    square_root = sqrt(number)

    # Check all numbers less than square root and see if it can be divided evenly
    numbers_to_check = list(range(1, int(square_root) + 1))

    for value in numbers_to_check:
        if number % value == 0 and value != 1:
            return False
    return True

# Prints out the first ten prime numbers that appear.
def first_ten_prime():
    prime_numbers = list()
    for number in range(2, 30):
        if is_prime(number):
            prime_numbers.append(number)

    for value in prime_numbers:
        print(value)

# Prints out the triangle value of 100
def triangle_of_100():
    sum = 0
    count = 0
    while count <= 100:
        sum += count
        count += 1

    return sum