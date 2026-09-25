import pytest
from src.task4 import calculate_discount


@pytest.mark.parametrize(
    "price, discount, expected",
    [
        (100, 10, 90),
        (50, 20, 40),
        (200, 25, 150),
        (75, 50, 37.5),
        (1000, 1, 990),
        (10.50, 10, 9.45),
        (99.99, 15, 84.9915),
        (500, 99, 5),
        (1, 50, 0.5),
        (100.0, 10.0, 90.0),
    ],
)
def test_calculate_discount_valid(price, discount, expected):
    assert calculate_discount(price, discount) == expected

@pytest.mark.parametrize(
    "price, discount",
    [
        (0, 10),
        (-1, 10),
        (-100, 25),
        (0.0, 50),
        (-0.5, 10),
    ],
)
def test_calculate_discount_invalid_price(price, discount):
    with pytest.raises(TypeError):
        calculate_discount(price, discount)

@pytest.mark.parametrize(
    "price, discount",
    [
        (100, 0),
        (100, -1),
        (100, 100),
        (100, 101),
        (100, 150),
        (50, 0.0),
        (50, 100.0),
    ],
)
def test_calculate_discount_invalid_discount(price, discount):
    with pytest.raises(TypeError):    
        assert calculate_discount(price, discount) is False

@pytest.mark.parametrize(
    "price, discount",
    [
        ("100", 10),
        (100, "10"),
        ("100", "10"),
        (None, 10),
        (100, None),
        ([], 10),
        (100, []),
    ],
)
def test_calculate_discount_invalid_types(price, discount):
    with pytest.raises(TypeError):
        assert calculate_discount(price, discount) is False