import math


# Check whether a transaction has a valid amount
def get_valid_amount(transaction):

    if len(transaction) < 6:
        return None

    try:
        amount = float(transaction[4])

    except (TypeError, ValueError):
        return None

    if not math.isfinite(amount) or amount < 0:
        return None

    return amount

# Calculate total income
def calculate_total_income(transactions):

    total_income = 0

    for transaction in transactions:

        amount = get_valid_amount(transaction)

        if amount is not None and transaction[2] == "Income":
            total_income += amount

    return total_income

# Calculate total expenses
def calculate_total_expenses(transactions):

    total_expenses = 0

    for transaction in transactions:

        amount = get_valid_amount(transaction)

        if amount is not None and transaction[2] == "Expense":
            total_expenses += amount

    return total_expenses

# Calculate remaining balance
def calculate_balance(total_income, total_expenses):

    return total_income - total_expenses

# Calculate expenses for a specific category and month
def calculate_category_expenses(transactions, category, budget_month):

    total = 0

    for transaction in transactions:

        if len(transaction) < 6:
            continue

        amount = get_valid_amount(transaction)

        if (
            amount is not None
            and transaction[2] == "Expense"
            and transaction[3] == category
            and isinstance(transaction[5], str)
            and transaction[5].startswith(budget_month)
        ):
            total += amount

    return total

# Calculate total expenses for a specific month
def calculate_monthly_expenses(transactions, budget_month):

    total = 0

    for transaction in transactions:

        if len(transaction) < 6:
            continue

        amount = get_valid_amount(transaction)

        if (
            amount is not None
            and transaction[2] == "Expense"
            and isinstance(transaction[5], str)
            and transaction[5].startswith(budget_month)
        ):
            total += amount

    return total

# Compare expenses between two months
def compare_monthly_expenses(transactions, current_month, previous_month):

    current_expenses = calculate_monthly_expenses(
        transactions, current_month
    )

    previous_expenses = calculate_monthly_expenses(
        transactions, previous_month
    )

    difference = current_expenses - previous_expenses

    if previous_expenses > 0:
        percentage_change = (difference / previous_expenses) * 100
    else:
        percentage_change = None

    return current_expenses, previous_expenses, difference, percentage_change
