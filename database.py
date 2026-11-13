import sqlite3
from pathlib import Path
from contextlib import contextmanager

#Connect to the database
def connect_db():
    database_path = Path(__file__).resolve().parent / "budget.db"

    print("Connecting to database:", database_path)

    connection = sqlite3.connect(database_path)
    return connection

@contextmanager
def db_connection():

    connection = connect_db()

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

#Create the transaction table
def create_table():

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_date TEXT NOT NULL
            )
        """)

#Update the database structure when necessary
def update_database():

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]

        if "transaction_date" not in columns:
            cursor.execute("""
                ALTER TABLE transactions
                ADD COLUMN transaction_date TEXT
            """)

#Add a new transaction
def add_transaction(description, transaction_type, category, amount, transaction_date):

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO transactions
            (description, transaction_type, category, amount, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            description,
            transaction_type,
            category,
            amount,
            transaction_date
        ))

#Retrieve all transaction
def get_transactions():

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                description,
                transaction_type,
                category,
                amount,
                transaction_date
            FROM transactions
            ORDER BY transaction_date DESC, id ASC
        """)

        transactions = cursor.fetchall()

        return transactions

#Delete a transaction
def delete_transaction(transaction_id):

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )


# Add or update a monthly budget
def save_budget(category, amount, budget_month):

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO budgets (category, amount, budget_month)
            VALUES (?, ?, ?)
            ON CONFLICT(category, budget_month)
            DO UPDATE SET amount = excluded.amount
        """, (category, amount, budget_month))


# Retrieve budgets for a specific month
def get_budgets(budget_month):

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, category, amount, budget_month
            FROM budgets
            WHERE budget_month = ?
            ORDER BY category ASC
        """, (budget_month,))

        budgets = cursor.fetchall()

        return budgets

# Delete a monthly budget
def delete_budget(budget_id):

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM budgets WHERE id = ?",
            (budget_id,)
        )

# Create the monthly budgets table
def create_budget_table():

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                budget_month TEXT NOT NULL,
                UNIQUE(category, budget_month)
            )
        """)