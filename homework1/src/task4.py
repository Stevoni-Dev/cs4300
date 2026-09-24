

# Reduce the price by a percentage equal to the discount
def calculate_discount(price, discount):
    price -= price * (discount / 100)
    return price