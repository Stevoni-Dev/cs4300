import pytest
from src.task4 import calculate_discount

valid_price_discounts = [(100, 20), (100.0, 20), (100, 20.0), (100.0, 20.0)]

@pytest.mark.parametrize(["price", "discount"], valid_price_discounts)
def test_calculate_discount_valid(price, discount):
    assert calculate_discount(price, discount) == 80