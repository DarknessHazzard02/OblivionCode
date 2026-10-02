"""
Simple Sales Summary
Made by: Hazzard
"""

sales = [1500, 2100, 1850, 3200, 2750]

total_sales = sum(sales)
average_sales = total_sales / len(sales)

print(f"Total Sales   : ${total_sales:,.2f}")
print(f"Average Sales : ${average_sales:,.2f}")
print(f"Records       : {len(sales)}")