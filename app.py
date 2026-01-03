
import streamlit as st
import pandas as pd
from oracle_db import login_user,register_user,add_transaction,get_user_transactions

st.set_page_config("📘 Accounting Dashboard", layout="wide")

if "user_id" not in st.session_state:
    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("✅ Registered. Please login.")
            else:
                st.error("⚠️ Username already exists.")
    st.stop()

st.sidebar.title("📊 Navigation")
menu = st.sidebar.radio("Go to", ["Add Journal Entry", "View Reports", "T-Ledgers", "Export CSV", "Logout"])

st.title(f"📒 Welcome, {st.session_state.username}")

if menu == "Add Journal Entry":
    st.subheader("➕ New Journal Entry")
    with st.form("entry_form"):
        date = st.date_input("Date")
        desc = st.text_input("Description")
        debit = st.text_input("Debit Account")
        debit_amt = st.number_input("Debit Amount", min_value=0.01, step=0.01)
        credit = st.text_input("Credit Account")
        credit_amt = st.number_input("Credit Amount", min_value=0.01, step=0.01)
        submitted = st.form_submit_button("Add Entry")

    if submitted:
        if debit_amt != credit_amt:
            st.error("⚠️ Debit and Credit must be equal!")
        else:
            add_transaction(st.session_state.user_id, {
                "date": str(date),
                "description": desc,
                "debit_account": debit,
                "debit_amount": debit_amt,
                "credit_account": credit,
                "credit_amount": credit_amt
            })
            st.success("✅ Transaction added.")

elif menu == "View Reports":
    st.subheader("📘 General Journal")
    df = get_user_transactions(st.session_state.user_id)
    st.dataframe(df, use_container_width=True)

elif menu == "T-Ledgers":
    st.subheader("📗 T-Ledgers")
    df = get_user_transactions(st.session_state.user_id)
    ledgers = {}
    for _, row in df.iterrows():
        for acc, val, typ in [(row['debit_account'], row['debit_amount'], 'Debit'),
                              (row['credit_account'], row['credit_amount'], 'Credit')]:
            if acc not in ledgers:
                ledgers[acc] = []
            ledgers[acc].append({
                'Date': row['txn_date'], 'Desc': row['description'],
                'Debit': val if typ == 'Debit' else '',
                'Credit': val if typ == 'Credit' else ''
            })
    for acc, entries in ledgers.items():
        st.markdown(f"### {acc}")
        st.dataframe(pd.DataFrame(entries), use_container_width=True)

elif menu == "Export CSV":
    df = get_user_transactions(st.session_state.user_id)
    st.subheader("📦 Export Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Journal CSV", csv, "journal.csv", "text/csv")

elif menu == "Logout":
    st.session_state.clear()
    st.experimental_rerun()
