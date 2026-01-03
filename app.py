import streamlit as st
import pandas as pd
from oracle_db import login_user, register_user, add_transaction, get_user_transactions

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="📘 Accounting Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Login / Register
# =========================
if "user_id" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>🔐 Login / Register</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.markdown("### Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials.", icon="⚠️")

    with tab2:
        st.markdown("### Create a new account")
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register", type="primary"):
            if register_user(new_user, new_pass):
                st.success("✅ Registered successfully. Please login.", icon="🎉")
            else:
                st.warning("⚠️ Username already exists.", icon="⚠️")
    st.stop()

# =========================
# Sidebar Navigation
# =========================
st.sidebar.markdown(f"### 📒 Welcome, {st.session_state.username}")
menu = st.sidebar.radio(
    "Navigate",
    ["Add Journal Entry", "View Reports", "T-Ledgers", "Export CSV", "Logout"]
)

# =========================
# Add Journal Entry Screen
# =========================
if menu == "Add Journal Entry":
    st.header("➕ New Journal Entry")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date")
            desc = st.text_input("Description")
        with col2:
            debit = st.text_input("Debit Account")
            debit_amt = st.number_input("Debit Amount", min_value=0.01, step=0.01)
            credit = st.text_input("Credit Account")
            credit_amt = st.number_input("Credit Amount", min_value=0.01, step=0.01)

        submitted = st.form_submit_button("Add Entry", type="primary")

    if submitted:
        if debit_amt != credit_amt:
            st.warning("⚠️ Debit and Credit must be equal!", icon="❌")
        else:
            add_transaction(st.session_state.user_id, {
                "date": str(date),
                "description": desc,
                "debit_account": debit,
                "debit_amount": debit_amt,
                "credit_account": credit,
                "credit_amount": credit_amt
            })
            st.success("✅ Transaction added successfully!", icon="🎉")

# =========================
# View Reports Screen
# =========================
elif menu == "View Reports":
    st.header("📘 General Journal")
    df = get_user_transactions(st.session_state.user_id)
    if df.empty:
        st.info("No transactions found.", icon="ℹ️")
    else:
        st.dataframe(df.style.format({
            "debit_amount": "${:,.2f}",
            "credit_amount": "${:,.2f}"
        }), use_container_width=True)

# =========================
# T-Ledgers Screen
# =========================
elif menu == "T-Ledgers":
    st.header("📗 T-Ledgers")
    df = get_user_transactions(st.session_state.user_id)
    if df.empty:
        st.info("No transactions found.", icon="ℹ️")
    else:
        ledgers = {}
        for _, row in df.iterrows():
            for acc, val, typ in [(row['debit_account'], row['debit_amount'], 'Debit'),
                                  (row['credit_account'], row['credit_amount'], 'Credit')]:
                if acc not in ledgers:
                    ledgers[acc] = []
                ledgers[acc].append({
                    'Date': row['txn_date'], 
                    'Desc': row['description'],
                    'Debit': f"${val:,.2f}" if typ == 'Debit' else "",
                    'Credit': f"${val:,.2f}" if typ == 'Credit' else ""
                })
        for acc, entries in ledgers.items():
            st.subheader(acc)
            st.dataframe(pd.DataFrame(entries), use_container_width=True)

# =========================
# Export CSV Screen
# =========================
elif menu == "Export CSV":
    st.header("📦 Export Journal Data")
    df = get_user_transactions(st.session_state.user_id)
    if df.empty:
        st.info("No transactions to export.", icon="ℹ️")
    else:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "journal.csv", "text/csv", use_container_width=True)

# =========================
# Logout
# =========================
elif menu == "Logout":
    st.session_state.clear()
    st.rerun()
