import psycopg2
import pandas as pd
from hashlib import sha256

# =============================
# DATABASE CONNECTION (Supabase)
# =============================
DATABASE_URL="postgresql://postgres.swwkwgfhmvdrfnbeipcs:[YOUR-PASSWORD]@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres"

connection = psycopg2.connect(
    DATABASE_URL,
    password="babychand67@#",
    sslmode="require"
)

# =============================
# PASSWORD HASHING
# =============================
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# =============================
# REGISTER USER
# =============================
def register_user(username, password):
    try:
        with connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO userzs (username, password)
                VALUES (%s, %s)
                """,
                (username, hash_password(password))
            )
            connection.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        return False

# =============================
# LOGIN USER
# =============================
def login_user(username, password):
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT user_id
            FROM userzs
            WHERE username = %s AND password = %s
            """,
            (username, hash_password(password))
        )
        row = cur.fetchone()
    return row[0] if row else None

# =============================
# ADD TRANSACTION
# =============================
def add_transaction(user_id, data):
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO transactions
            (user_id, txn_date, description,
             debit_account, debit_amount,
             credit_account, credit_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                data["date"],
                data["description"],
                data["debit_account"],
                data["debit_amount"],
                data["credit_account"],
                data["credit_amount"]
            )
        )
        connection.commit()

# =============================
# FETCH TRANSACTIONS
# =============================
def get_user_transactions(user_id):
    query = """
    SELECT
        txn_date,
        description,
        debit_account,
        debit_amount,
        credit_account,
        credit_amount
    FROM transactions
    WHERE user_id = %s
    ORDER BY txn_date
    """
    return pd.read_sql(query, con=connection, params=(user_id,))
cur = connection.cursor()
cur.execute("SELECT now();")
print(cur.fetchone())
