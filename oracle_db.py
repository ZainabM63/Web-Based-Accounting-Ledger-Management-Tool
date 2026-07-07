import psycopg2
import pandas as pd
from hashlib import sha256

# =============================
# DATABASE CONNECTION (Neon)
# =============================
connection = None

def get_connection():
    global connection
    try:
        cur = connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
    except (psycopg2.InterfaceError, psycopg2.OperationalError, AttributeError):
        connection = psycopg2.connect(
            host="ep-bitter-glitter-at1ilmu3-pooler.c-9.us-east-1.aws.neon.tech",
            port=5432,
            database="neondb",
            user="neondb_owner",
            password="npg_wRnHDa5IQfr7",
            sslmode="require"
        )
        _init_tables(connection)
    return connection

def _init_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS userzs (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(64) NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id INT REFERENCES userzs(user_id),
                txn_date DATE,
                description TEXT,
                debit_account VARCHAR(255),
                debit_amount NUMERIC(12,2),
                credit_account VARCHAR(255),
                credit_amount NUMERIC(12,2)
            )
        """)
        conn.commit()

get_connection()

# =============================
# PASSWORD HASHING
# =============================
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# =============================
# REGISTER USER
# =============================
def register_user(username, password):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO userzs (username, password)
                VALUES (%s, %s)
                """,
                (username, hash_password(password))
            )
            conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False

# =============================
# LOGIN USER
# =============================
def login_user(username, password):
    conn = get_connection()
    with conn.cursor() as cur:
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
    conn = get_connection()
    with conn.cursor() as cur:
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
        conn.commit()

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
    return pd.read_sql(query, con=get_connection(), params=(user_id,))
cur = get_connection().cursor()
cur.execute("SELECT now();")
print(cur.fetchone())
