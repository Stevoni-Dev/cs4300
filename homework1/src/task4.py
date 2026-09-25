

# Reduce the price by a percentage equal to the discount
def calculate_discount(price, discount):
    if not (
        hasattr(price, "__mul__")
        and hasattr(price, "__truediv__")
        and hasattr(discount, "__mul__")
        and hasattr(discount, "__truediv__")
        ):
        raise TypeError("Provide objects that can support division and multiplication")

    if price <= 0:
        raise TypeError("Invalid price amount")
    if discount <= 0 or discount >= 100:
        raise TypeError("Invalid discount amount")
    price -= price * (discount / 100)
    return price