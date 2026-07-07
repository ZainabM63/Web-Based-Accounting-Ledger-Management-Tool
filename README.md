
# Developer

**Zainab Mughal**


# Web-Based Accounting Ledger Management Tool

A comprehensive web-based application for managing accounting ledgers, tracking transactions, and maintaining financial records. This tool allows users to register, log in, add transactions, and view their transaction history in an organized manner.

---

## Features

- **User Management**
  - Register new users with secure password hashing
  - Login functionality with hashed password authentication

- **Transaction Management**
  - Add debit and credit transactions
  - Record transaction date, description, and accounts
  - View transaction history in a tabular format

- **Security**
  - Passwords are hashed using SHA-256
  - Database connections secured using SSL (Neon PostgreSQL)

- **Database Integration**
  - Uses Neon PostgreSQL for data storage (always-on, no 7-day pause)
  - Supports multiple users and transactions
  - Fetches transactions using SQL queries with pandas
  - Auto-creates tables on startup (no manual schema setup required)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ZainabM63/Web-Based-Accounting-Ledger-Management-Tool.git
````

2. Navigate to the project directory:

   ```bash
   cd expense_tracker_oracle
   ```

3. Install required Python packages:

   ```bash
   pip install psycopg2-binary pandas
   ```

4. Update the database credentials in `oracle_db.py` with your Neon connection string.

---

## Usage

* Run the test script to verify the database connection:

  ```bash
  python test.py
  ```

* Use the provided functions to register users, log in, add transactions, and fetch transaction history.

---

## Project Structure

```
expense_tracker_oracle/
├── app.py                 # Main Streamlit application
├── oracle_db.py           # Database connection and CRUD operations
├── test.py                # Test database connection
├── index.html             # Netlify embed wrapper
├── netlify.toml           # Netlify deployment config
├── setup.sh               # Streamlit Cloud setup script
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
```


---
