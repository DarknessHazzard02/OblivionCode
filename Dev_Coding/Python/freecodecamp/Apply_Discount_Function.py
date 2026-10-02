def apply_discount(price, discount):
    if type(price) not in (int, float):
        return "The price should be a number"
        
    if type(discount) not in (int, float):
        return "The discount should be a number"
        
    if price <= 0:
        return "The price should be greater than 0"
        
    if discount < 0 or discount > 100:
        return "The discount should be between 0 and 100"
        
    discount_amount = price * (discount / 100)
    return price - discount_amount

print(apply_discount(2250, 15))