

# Reduce the price by a percentage equal to the discount
def calculate_discount(price, discount):
    if not (
        hasattr(price, "__mul__")
        and hasattr(price, "__truediv__")
        and hasattr(discount, "__mul__")
        and hasattr(discount, "__truediv__")
        ):
        print("Provide objects that can support division and multiplication")
        return False
    if price <= 0:
        print("Invalid price amount")
        return False
    if discount <= 0 or discount >= 100:
        print("Invalid discount amount")
        return False
    price -= price * (discount / 100)
    return price