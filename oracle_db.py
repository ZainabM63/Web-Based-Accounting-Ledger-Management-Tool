
import oracledb
import pandas as pd
from hashlib import sha256

# Enable thin mode (no Oracle Client needed)
oracledb.init_oracle_client(lib_dir=None)  # Optional if thin mode is fine

# Connection
dsn = oracledb.makedsn("localhost", 1521, service_name="orcl")  # Update as needed
connection = oracledb.connect(
    user="sys",
    password="Uit54321",
    dsn=dsn,
    mode=oracledb.SYSDBA
)

# Password hashing
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Register user
def register_user(username, password):
    try:
        with connection.cursor() as cur:
            cur.execute("INSERT INTO userzs (username, password) VALUES (:1, :2)",
                        (username, hash_password(password)))
            connection.commit()
        return True
    except oracledb.IntegrityError:
        return False

# Login user
def login_user(username, password):
    with connection.cursor() as cur:
        cur.execute("SELECT user_id FROM userzs WHERE username = :1 AND password = :2",
                    (username, hash_password(password)))
        row = cur.fetchone()
    return row[0] if row else None

# Add transaction
def add_transaction(user_id, data):
    with connection.cursor() as cur:
        cur.execute('''INSERT INTO transactions 
                       (user_id, txn_date, description, debit_account, debit_amount, credit_account, credit_amount)
                       VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7)''',
                    (user_id, data["date"], data["description"], data["debit_account"], data["debit_amount"],
                     data["credit_account"], data["credit_amount"]))
        connection.commit()

# Get all user transactions as DataFrame
def get_user_transactions(user_id):
    query = """
    SELECT txn_date AS "txn_date",
           description AS "description",
           debit_account AS "debit_account",
           debit_amount AS "debit_amount",
           credit_account AS "credit_account",
           credit_amount AS "credit_amount"
    FROM transactions
    WHERE user_id = :user_id
    ORDER BY txn_date
    """
    return pd.read_sql(query, con=connection, params={"user_id": user_id})
def update_transaction(txn_id, updated_data):
    with connection.cursor() as cur:
        cur.execute("""
            UPDATE transactions SET
                txn_date = :1,
                description = :2,
                debit_account = :3,
                debit_amount = :4,
                credit_account = :5,
                credit_amount = :6
            WHERE txn_id = :7
        """, (
            updated_data["date"],
            updated_data["description"],
            updated_data["debit_account"],
            updated_data["debit_amount"],
            updated_data["credit_account"],
            updated_data["credit_amount"],
            txn_id
        ))
        connection.commit()

def delete_transaction(txn_id):
    with connection.cursor() as cur:
        cur.execute("DELETE FROM transactions WHERE txn_id = :1", (txn_id,))
        connection.commit()

