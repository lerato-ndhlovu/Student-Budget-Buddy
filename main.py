import flet as ft
import math

from datetime import date, datetime, timedelta

from database import (
    save_budget,
    get_budgets,
    delete_budget,
    create_table,
    update_database,
    add_transaction,
    get_transactions,
    delete_transaction,
    create_budget_table,
)

from calculations import (
    get_valid_amount,
    calculate_total_income,
    calculate_total_expenses,
    calculate_balance,
    calculate_category_expenses,
    compare_monthly_expenses,
)

def main(page: ft.Page):

    #Page configuration
    page.title = "Student Budget Buddy"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F7FB"
    page.padding = 0

    create_table()
    update_database()
    #migrate_database(),
    create_budget_table()

    #Dashboard summary cards
    def summary_cards(title, amount, description, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=14, color="#64748B"),
                    ft.Text(
                        amount,
                        size=26,
                        weight=ft.FontWeight.BOLD, 
                        color=color
                    ),
                    ft.Text(description, size=13, color="#64748B")
                ],
                spacing=8
            ),
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=12,
            expand=True
        )

    #Main content sections
    def show_dashboard():

        # Retrieve all saved transactions
        transactions = get_transactions()

        # Calculate financial totals
        total_income = calculate_total_income(transactions)
        total_expenses = calculate_total_expenses(transactions)
        balance = calculate_balance(total_income, total_expenses)

        return ft.Column(
            controls=[
                ft.Text(
                    "Dashboard",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),
                ft.Text(
                    "Welcome back! Here's your financial overview.",
                    color="#647488"
                ),
                ft.Row(
                    controls=[
                        summary_cards(
                            "Total Income", f"R {total_income:,.2f}",
                            "Money received", "#16A34A"
                        ),
                        summary_cards(
                            "Total Expenses", f"R {total_expenses:,.2f}",
                            "Money spent", "#DC2626"
                        ),
                        summary_cards(
                            "Remaining Balance",f"R {balance:,.2f}",
                            "Available funds", "#172554"
                        )
                    ],
                    spacing=15
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Welcome to Student Budget Buddy!"
                                if not transactions
                                else "Your Financial Overview",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="#172554"
                            ),
                            ft.Text(
                                "Start recording your income and expenses "
                                "to understand your spending."
                                if not transactions
                                else "Keep tracking your income and expenses "
                                    "to stay on top of your finances.",
                                color="#64748B"
                            )
                        ],
                        spacing=10
                    ),
                    bgcolor="#FFFFFF",
                    padding=25,
                    border_radius=12
                )
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def show_transactions(message=""):

        #Input fields
        description_field = ft.TextField(
            label="Description",
            hint_text="e.g. Monthly allowance",
            width=350
        )

        amount_field = ft.TextField(
            label="Amount (R)",
            hint_text="e.g. 1500",
            width=350,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        type_dropdown = ft.Dropdown(
            label="Transaction Type",
            width=350,
            value=None,
            options=[
                ft.DropdownOption("Income", "Income"),
                ft.DropdownOption("Expense", "Expense")
            ]
        )

        category_dropdown = ft.Dropdown(
            label="Category",
            width=350,
            value=None,
            options=[
                ft.DropdownOption("Allowance", "Allowance"),
                ft.DropdownOption("Bursary", "Bursary"),
                ft.DropdownOption("Part-time Work", "Part-time Work"),
                ft.DropdownOption("Accommodation", "Accommodation"),
                ft.DropdownOption("Groceries", "Groceries"),
                ft.DropdownOption("Transport", "Transport"),
                ft.DropdownOption("University Expenses", "University Expenses"),
                ft.DropdownOption("Data and Airtime", "Data and Airtime"),
                ft.DropdownOption("Personal Care", "Personal Care"),
                ft.DropdownOption("Entertainment", "Entertainment"),
                ft.DropdownOption("Savings", "Savings"),
                ft.DropdownOption("Other", "Other"),
            ]
        )

        date_field = ft.TextField(
            label="Transaction Date (YYYY-MM-DD)",
            value=date.today().isoformat(),
            width=350
        )

        feedback = ft.Text(
            message,
            color="#16A34A" if message else "#DC2626"
        )

        #Save transaction
        def save_transaction(e):

            description = description_field.value.strip()
            amount = amount_field.value.strip()
            transaction_type = type_dropdown.value
            category = category_dropdown.value
            transaction_date = date_field.value.strip()

            #Validate inputs
            if (
                not description
                or not amount
                or not transaction_date
                or not transaction_type
                or not category
            ):
                feedback.value = "Please complete all fields."
                feedback.color = "#DC2626"
                page.update()
                return

            try:
                amount = float(amount)

                if not math.isfinite(amount):
                    feedback.value = "Please enter a valid finite amount."
                    feedback.color = "#DC2626"
                    page.update()
                    return

                if amount <= 0:
                    feedback.value = "Amount must be greater than zero."
                    feedback.color = "#DC2626"
                    page.update()
                    return

            except ValueError:
                feedback.value = "Please enter a valid numerical amount."
                feedback.color = "#DC2626"
                page.update()
                return

            #Check date format
            from datetime import date

            try:
                selected_date = date.fromisoformat(transaction_date)

                if selected_date > date.today():
                    feedback.value = "Transaction date cannot be in the future."
                    feedback.color = "#DC2626"
                    page.update()
                    return
    
            except ValueError:
                feedback.value = "Enter a valid date (YYYY-MM-DD)."
                feedback.color = "#DC2626"
                page.update()
                return

            # Save transaction to database
            add_transaction(
                description,
                transaction_type,
                category,
                amount,
                transaction_date
            )

            # Refresh transaction page
            content_area.content = show_transactions(
                "Transaction saved successfully!"
            )

            page.update()

        #Confirm transaction deletion
        def handle_delete(e):

            transaction_id = e.control.data

            # Delete only after confirmation
            def confirm_delete(e):
                
                page.pop_dialog()

                delete_transaction(transaction_id)

                content_area.content = show_transactions(
                    "Transaction deleted successfully!"
                )

                page.update()

            # Cancel deletion
            def cancel_delete(e):

                page.pop_dialog()

            delete_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Deletion"),
                content=ft.Text(
                    "Are you sure you want to delete this transaction? "
                    "This action cannot be undone."
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=cancel_delete
                    ),
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

            page.show_dialog(delete_dialog)

        #Retrieve saved transaction
        transactions = get_transactions()

        #Create transaction table
        transaction_rows = []

        for transaction in transactions:

            transaction_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(transaction[0]))),
                        ft.DataCell(ft.Text(transaction[1])),
                        ft.DataCell(ft.Text(transaction[2])),
                        ft.DataCell(ft.Text(transaction[3])),
                        ft.DataCell(ft.Text(f"R {transaction[4]:,.2f}")),
                        ft.DataCell(ft.Text(transaction[5])),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color="#DC2626",
                                data=transaction[0],
                                on_click=handle_delete
                            )
                        )
                    ]
                )
            )

        #Transactions page layout
        return ft.Column(
            controls=[
                ft.Text(
                    "Transactions",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                ft.Text(
                    "Record and manage your income and expenses.",
                    color="#64748B"
                ),

                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Add New Transaction",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="#172554"
                            ),

                            description_field,
                            type_dropdown,
                            category_dropdown,
                            amount_field,
                            date_field,

                            ft.Button(
                                content="Save Transaction",
                                icon=ft.Icons.ADD,
                                on_click=save_transaction
                            ),

                            feedback

                        ],
                        spacing=15
                    ),
                    bgcolor="#FFFFFF",
                    padding=25,
                    border_radius=12
                ),

                ft.Text(
                    "Transaction History",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("ID")),
                                    ft.DataColumn(ft.Text("Description")),
                                    ft.DataColumn(ft.Text("Type")),
                                    ft.DataColumn(ft.Text("Category")),
                                    ft.DataColumn(ft.Text("Amount")),
                                    ft.DataColumn(ft.Text("Date")),
                                    ft.DataColumn(ft.Text("Delete"))
                                ],
                                rows=transaction_rows,
                                column_spacing=20
                            )
                        ],
                        scroll=ft.ScrollMode.AUTO
                    ),
                    width=float("inf")
                ) if transaction_rows else ft.Text(
                    "No transactions recorded yet.",
                    color="#64748B"
                )
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def show_budget(selected_month=None, message=None):

        # Get the current month
        if selected_month is None:
            current_month = date.today().strftime("%Y-%m")
        else:
            current_month = selected_month

        # Month selection handler
        def handle_month_change(e):
            selected_month = month_dropdown.value
            content_area.content = show_budget(selected_month)
            page.update()

        # Generate month options dynamically
        today = date.today()
        month_options = []

        for offset in range(-12, 13):

            month_index = today.month - 1 + offset

            year = today.year + month_index // 12
            month = month_index % 12 + 1

            month_value = f"{year}-{month:02d}"
            month_label = date(year, month, 1).strftime("%B %Y")

            month_options.append(
                ft.DropdownOption(month_value, month_label)
            )

        # Month selector
        month_dropdown = ft.Dropdown(
            label="Select Month",
            value=current_month,
            options=month_options,
            width=300,
            on_select=handle_month_change
        )

        amount_field = ft.TextField(
            label="Monthly Budget Amount (R)",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=350
        )

        category_dropdown = ft.Dropdown(
                    label="Category",
                    width=350,
                    options=[
                        ft.DropdownOption("Accommodation", "Accommodation"),
                        ft.DropdownOption("Groceries", "Groceries"),
                        ft.DropdownOption("Transport", "Transport"),
                        ft.DropdownOption("University Expenses", "University Expenses"),
                        ft.DropdownOption("Data and Airtime", "Data and Airtime"),
                        ft.DropdownOption("Personal Care", "Personal Care"),
                        ft.DropdownOption("Entertainment", "Entertainment"),
                        ft.DropdownOption("Other", "Other")
                    ]
        )

        feedback_text = ft.Text(
            message or "",
            color="#16A34A" if message else None
        )

        # Save budget
        def handle_save_budget(e):

            amount = amount_field.value.strip()
            category = category_dropdown.value

            # Validate category
            if not category:
                feedback_text.value = "Please select a category."
                feedback_text.color = "#DC2626"
                page.update()
                return

            # Validate empty amount
            if not amount:
                feedback_text.value = "Please enter a budget amount."
                feedback_text.color = "#DC2626"
                page.update()
                return

            # Validate numerical amount
            try:
                amount = float(amount)

                if not math.isfinite(amount):
                    feedback_text.value = "Please enter a valid finite budget amount."
                    feedback_text.color = "#DC2626"
                    page.update()
                    return

            except ValueError:
                feedback_text.value = "Please enter a valid numerical amount."
                feedback_text.color = "#DC2626"
                page.update()
                return

            # Validate positive amount
            if amount <= 0:
                feedback_text.value = "Budget amount must be greater than zero."
                feedback_text.color = "#DC2626"
                page.update()
                return

            # Save budget
            save_budget(category, amount, current_month)

            # Clear amount field
            amount_field.value = ""

            # Refresh while preserving selected month
            content_area.content = show_budget(
                current_month,
                "Budget saved successfully!"
            )

            page.update()

         # Delete a monthly budget
        def handle_delete_budget(e):

            budget_id = e.control.data

            def confirm_delete(e):

                page.pop_dialog()

                delete_budget(budget_id)

                content_area.content = show_budget(
                    current_month,
                    "Budget deleted successfully!"
                )

                page.update()

            def cancel_delete(e):
                page.pop_dialog()

            delete_dialog = ft.AlertDialog(
                title=ft.Text("Delete Budget"),
                content=ft.Text(
                    "Are you sure you want to delete this budget?"
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=cancel_delete
                    ),
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete
                    )
                ]
            )

            page.show_dialog(delete_dialog)

        # Retrieve saved budgets
        budgets = get_budgets(current_month)
        transactions = get_transactions()

        current_date = datetime.strptime(current_month, "%Y-%m")

        previous_month = (
            current_date.replace(day=1) - timedelta(days=1)
        ).strftime("%Y-%m")

        # Compare monthly expenses
        comparison = compare_monthly_expenses(
            transactions,
            current_month,
            previous_month
        )

        current_expenses, previous_expenses, difference, percentage_change = comparison

        total_budget = 0
        total_spent = 0

        for budget in budgets:
            total_budget += budget[2]

            total_spent += calculate_category_expenses(
                transactions,
                budget[1],
                budget[3]
            )

        total_remaining = total_budget - total_spent

        # Display saved budgets
        budget_rows = []

        for budget in budgets:
            category = budget[1]
            budget_amount = budget[2]
            budget_month = budget[3]

            spent = calculate_category_expenses(
                transactions,
                category,
                budget_month
            )

            remaining = budget_amount - spent

            # Calculate budget progress safely
            if budget_amount > 0:
                progress = spent / budget_amount
                progress_percentage = (spent / budget_amount) * 100
            else:
                progress = 0
                progress_percentage = 0

            # Prevent progress bar from exceeding 100%
            progress = min(progress, 1)

            # Determine progress colour and status
            if budget_amount <= 0:
                progress_color = "#DC2626"
                budget_status = "Invalid Budget"

            elif spent >= budget_amount:
                progress_color = "#DC2626"
                budget_status = "Budget Exceeded"

            elif progress >= 0.75:
                progress_color = "#D97706"
                budget_status = "Almost at Limit"

            else:
                progress_color = "#16A34A"
                budget_status = "Within Budget"

            budget_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(category)),

                        ft.DataCell(
                            ft.Text(f"R {budget_amount:,.2f}")
                        ),

                        ft.DataCell(
                            ft.Column(
                                controls=[
                                    ft.Text(f"R {spent:,.2f}"),
                                    ft.ProgressBar(
                                        value=progress,
                                        color=progress_color,
                                        bgcolor="#E2E8F0"
                                    ),
                                    ft.Text(
                                        f"{progress_percentage:.1f}%",
                                        size=12,
                                        color=progress_color,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ],
                                spacing=5
                            )
                        ),

                        ft.DataCell(
                            ft.Text(
                                f"R {remaining:,.2f}",
                                color="#DC2626" if remaining < 0 else "#16A34A"
                            )
                        ),

                        ft.DataCell(
                            ft.Text(
                                budget_status,
                                color=progress_color,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color="#DC2626",
                                tooltip="Delete Budget",
                                data=budget[0],
                                on_click=handle_delete_budget
                            )
                        )
                    ]
                )
            )

        # Budget table
        if budget_rows:

            budget_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Category")),
                    ft.DataColumn(ft.Text("Monthly Budget")),
                    ft.DataColumn(ft.Text("Amount Spent")),
                    ft.DataColumn(ft.Text("Remaining")),
                    ft.DataColumn(ft.Text("Status")),
                    ft.DataColumn(ft.Text("Action"))
                ],
                rows=budget_rows
            )

        else:
            budget_table = ft.Text(
                "No budgets have been created for this month yet.",
                color="#64748B"
            )

        summary_section = ft.Row(
            controls=[
                ft.Container(
                    content=summary_cards(
                        "Total Budget",
                        f"R {total_budget:,.2f}",
                        "Your monthly budget limits",
                        "#2563EB"
                    ),
                    expand=True
                ),
                ft.Container(
                    content=summary_cards(
                        "Total Spent",
                        f"R {total_spent:,.2f}",
                        "Spent across budget categories",
                        "#D97706"
                    ),
                    expand=True
                ),
                ft.Container(
                    content=summary_cards(
                        "Remaining Budget",
                        f"R {total_remaining:,.2f}",
                        "Budget available to spend",
                        "#16A34A" if total_remaining >= 0 else "#DC2626"
                    ),
                    expand=True
                )
            ],
            spacing=15
        )

        # Monthly spending comparison
        if current_expenses == 0 and previous_expenses == 0:
            comparison_color = "#64748B"
            comparison_status = "No expenses recorded in either month"
            percentage_text = "Nothing to compare yet"

        elif previous_expenses == 0:
            comparison_color = "#64748B"
            comparison_status = "No previous spending to compare"
            percentage_text = "No previous spending to compare"

        elif difference > 0:
            comparison_color = "#DC2626"
            comparison_status = "Your spending increased"
            percentage_text = (
                f"{abs(percentage_change):.1f}% - {comparison_status}"
            )

        elif difference < 0:
            comparison_color = "#16A34A"
            comparison_status = "Your spending decreased"
            percentage_text = (
                f"{abs(percentage_change):.1f}% - {comparison_status}"
            )

        else:
            comparison_color = "#64748B"
            comparison_status = "Your spending stayed the same"
            percentage_text = (
                f"{abs(percentage_change):.1f}% - {comparison_status}"
            )

        comparison_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Monthly Spending Comparison",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="#172554"
                    ),
                    ft.Text(
                        f"Current month: R {current_expenses:,.2f}",
                        size=14
                    ),
                    ft.Text(
                        f"Previous month: R {previous_expenses:,.2f}",
                        size=14
                    ),
                    ft.Text(
                        f"Difference: R {abs(difference):,.2f}",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=comparison_color
                    ),
                    ft.Text(
                        percentage_text,
                        size=14,
                        color=comparison_color
                    )
                ],
                spacing=10
            ),
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=12
        )

        return ft.Column(
            controls=[
                ft.Text(
                    "Budget Planner",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                ft.Text(
                    "Plan your monthly spending and monitor your limits.",
                    color="#64748B"
                ),

                summary_section,
                month_dropdown,
                comparison_card,

                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Create a Monthly Budget",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="#172554"
                            ),

                            category_dropdown,
                            amount_field,

                            ft.Button(
                                content="Save Budget",
                                icon=ft.Icons.SAVE,
                                on_click=handle_save_budget
                            ),

                            feedback_text
                        ],
                        spacing=15
                    ),
                    bgcolor="#FFFFFF",
                    padding=20,
                    border_radius=12
                ),

                ft.Text(
                    "Your Monthly Budgets",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                ft.Container(
                    content=ft.Row(
                        controls=[budget_table],
                        scroll=ft.ScrollMode.AUTO
                    ),
                    expand=True
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def show_reports():
        
        # Retrieve transactions
        transactions = get_transactions()

        # Calculate financial totals
        total_income = calculate_total_income(transactions)
        total_expenses = calculate_total_expenses(transactions)
        balance = calculate_balance(total_income, total_expenses)

        # Calculate expenses by category
        category_totals = {}

        for transaction in transactions:

            if transaction[2] == "Expense":

                category = transaction[3]
                amount = transaction[4]

                if category in category_totals:
                    category_totals[category] += amount
                else:
                    category_totals[category] = amount

        # Create expense breakdown rows
        category_rows = []

        for category, amount in category_totals.items():

            category_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(category)),
                        ft.DataCell(ft.Text(f"R {amount:,.2f}"))
                    ]
                )
            )

        # Expense breakdown table
        if category_rows:

            expense_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Category")),
                    ft.DataColumn(ft.Text("Total Spent"))
                ],
                rows=category_rows
            )

        else:
            expense_table = ft.Text(
                "No expenses have been recorded yet.",
                color="#64748B"
            )

        # Calculate expenses by category and monthly totals
        category_totals = {}
        monthly_totals = {}

        for transaction in transactions:

            if len(transaction) < 6:
                continue

            amount = get_valid_amount(transaction)
            transaction_type = transaction[2]
            category = transaction[3]
            transaction_date = transaction[5]

            # Skip invalid amounts and transaction types
            if amount is None:
                continue

            if transaction_type not in ("Income", "Expense"):
                continue

            # Calculate expenses by category
            if transaction_type == "Expense":

                if category in category_totals:
                    category_totals[category] += amount
                else:
                    category_totals[category] = amount

            # Calculate monthly totals only when a valid date exists
            if (
                isinstance(transaction_date, str)
                and len(transaction_date) >= 7
            ):

                month = transaction_date[:7]

                if month not in monthly_totals:
                    monthly_totals[month] = {
                        "Income": 0,
                        "Expense": 0
                    }

                monthly_totals[month][transaction_type] += amount

        # Create monthly comparison rows
        monthly_comparison_rows = []

        for month, totals in sorted(monthly_totals.items()):

            income = totals["Income"]
            expenses = totals["Expense"]

            monthly_comparison_rows.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                month,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#172554"
                            ),
                            ft.Text(
                                f"Income: R {income:,.2f}",
                                color="#16A34A"
                            ),
                            ft.ProgressBar(
                                value=income / max(income, expenses, 1),
                                color="#16A34A",
                                bgcolor="#E2E8F0",
                            ),
                            ft.Text(
                                f"Expenses: R {expenses:,.2f}",
                                color="#D97706"
                            ),
                            ft.ProgressBar(
                                value=expenses / max(income, expenses, 1),
                                color="#D97706",
                                bgcolor="#E2E8F0"
                            )
                        ],
                        spacing=8
                    ),
                    bgcolor="#FFFFFF",
                    padding=15,
                    border_radius=12
                )
            )

        if monthly_comparison_rows:
            monthly_comparison_content = ft.Column(
                controls=monthly_comparison_rows,
                spacing=10
            )
        else:
            monthly_comparison_content = ft.Text(
                "No monthly transaction data is available yet.",
                color="#64748B"
            )

        # Find the highest category expense
        max_category_expense = max(category_totals.values(), default=0)

        # Create visual expense breakdown
        category_progress_rows = []

        for category, amount in category_totals.items():

            if max_category_expense > 0:
                progress = amount / max_category_expense
            else:
                progress = 0

            category_progress_rows.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        category,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(f"R {amount:,.2f}")
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.ProgressBar(
                                value=progress,
                                color="#2563EB",
                                bgcolor="#E2E8F0"
                            )
                        ],
                        spacing=8
                    ),
                    padding=10
                )
            )

        if category_progress_rows:
            category_breakdown_content = ft.Column(
                controls=category_progress_rows,
                spacing=10
            )
        else:
            category_breakdown_content = ft.Text(
                "No expense data is available for a visual breakdown yet.",
                color="#64748B"
            )
        

        # Financial summary cards
        summary_section = ft.Row(
            controls=[
                ft.Container(
                    content=summary_cards(
                        "Total Income",
                        f"R {total_income:,.2f}",
                        "All recorded income",
                        "#16A34A"
                    ),
                    expand=True
                ),

                ft.Container(
                    content=summary_cards(
                        "Total Expenses",
                        f"R {total_expenses:,.2f}",
                        "All recorded expenses",
                        "#D97706"
                    ),
                    expand=True
                ),

                ft.Container(
                    content=summary_cards(
                        "Remaining Balance",
                        f"R {balance:,.2f}",
                        "Income minus expenses",
                        "#2563EB" if balance >= 0 else "#DC2626"
                    ),
                    expand=True
                )
            ],
            spacing=15
        )

        return ft.Column(
            controls=[
                ft.Text(
                    "Financial Reports",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                ft.Text(
                    "Understand your financial habits through reports.",
                    color="#64748B"
                ),

                summary_section,

                ft.Text(
                    "Expense Breakdown by Category",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                expense_table,

                ft.Text(
                    "Visual Expense Breakdown",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                ft.Container(
                    content=category_breakdown_content,
                    bgcolor="#FFFFFF",
                    padding=15,
                    border_radius=12
                ),
                
                ft.Text(
                    "Monthly Income vs Expenses",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#172554"
                ),

                monthly_comparison_content,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    #Navigation
    selected_section = "Dashboard"

    content_area = ft.Container(
        content=show_dashboard(),
        expand=True,
        padding=30
    )

    def navigate(section):
        nonlocal selected_section

        sections = {
            "Dashboard": show_dashboard,
            "Transactions": show_transactions,
            "Budget Planner": show_budget,
            "Financial Reports": show_reports
        }

        selected_section = section

        content_area.content = sections[section]()

        sidebar.content = build_sidebar()

        page.update()


    def navigation_item(label, icon):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color="#FFFFFF", size=20),
                    ft.Text(label, color="#FFFFFF", size=14)
                ],
                spacing=12
            ),
            padding=12,
            border_radius=8,
            bgcolor="#334155" if label == selected_section else None,
            ink=True,
            on_click=lambda e: navigate(label)
        )


    def build_sidebar():
        return ft.Column(
            controls=[
                ft.Text(
                    "Student Budget",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF"
                ),
                ft.Text(
                    "BUDDY",
                    size=13,
                    color="#86EFAC",
                    weight=ft.FontWeight.BOLD
                ),
                ft.Divider(color="#475569"),
                navigation_item("Dashboard", ft.Icons.DASHBOARD),
                navigation_item("Transactions", ft.Icons.RECEIPT_LONG),
                navigation_item(
                    "Budget Planner",
                    ft.Icons.ACCOUNT_BALANCE_WALLET
                ),
                navigation_item(
                    "Financial Reports",
                    ft.Icons.BAR_CHART
                )
            ],
            spacing=12
        )


    sidebar = ft.Container(
        content=build_sidebar(),
        width=240,
        bgcolor="#172554",
        padding=20
    )
    #Application layout
    page.add(
        ft.Row(
            controls=[
                sidebar,
                content_area
            ],
            spacing=0,
            expand=True
        )
    )

    

ft.run(main)