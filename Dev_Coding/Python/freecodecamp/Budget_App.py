# FreeCodeCamp Scientific Computing with Python - Budget App
# Object-oriented Category class managing deposits, withdrawals, transfers, balances, and spend charts

class Category:
    def __init__(self, name):
        self.name = name
        self.ledger = []

    def deposit(self, amount, description=""):
        self.ledger.append({"amount": amount, "description": description})

    def withdraw(self, amount, description=""):
        if self.check_funds(amount):
            self.ledger.append({"amount": -amount, "description": description})
            return True
        return False

    def get_balance(self):
        return sum(item["amount"] for item in self.ledger)

    def transfer(self, amount, target_category):
        if self.check_funds(amount):
            self.withdraw(amount, f"Transfer to {target_category.name}")
            target_category.deposit(amount, f"Transfer from {self.name}")
            return True
        return False

    def check_funds(self, amount):
        return self.get_balance() >= amount

    def __str__(self):
        title = f"{self.name:*^30}\n"
        items = ""
        for entry in self.ledger:
            desc = entry["description"][:23].ljust(23)
            amt = f"{entry['amount']:.2f}".rjust(7)
            items += f"{desc}{amt}\n"
        total = f"Total: {self.get_balance():.2f}"
        return title + items + total


def create_spend_chart(categories):
    spent = []
    for cat in categories:
        withdrawals = sum(-item["amount"] for item in cat.ledger if item["amount"] < 0)
        spent.append(withdrawals)

    total_spent = sum(spent)
    percentages = [int((amount / total_spent) * 100) // 10 * 10 if total_spent > 0 else 0 for amount in spent]

    chart = "Percentage spent by category\n"
    for i in range(100, -1, -10):
        chart += f"{str(i).rjust(3)}| "
        for p in percentages:
            chart += "o  " if p >= i else "   "
        chart += "\n"

    chart += "    -" + "---" * len(categories) + "\n"

    max_len = max(len(cat.name) for cat in categories)
    names = [cat.name.ljust(max_len) for cat in categories]

    for i in range(max_len):
        chart += "     "
        for name in names:
            chart += f"{name[i]}  "
        if i < max_len - 1:
            chart += "\n"

    return chart


# Demo
food = Category("Food")
food.deposit(1000, "initial deposit")
food.withdraw(10.15, "groceries")
food.withdraw(15.89, "restaurant and more food")

clothing = Category("Clothing")
food.transfer(50, clothing)
clothing.withdraw(25.55, "jacket")

auto = Category("Auto")
auto.deposit(1000, "initial deposit")
auto.withdraw(15, "gas")

print(food)
print("\n" + create_spend_chart([food, clothing, auto]))
