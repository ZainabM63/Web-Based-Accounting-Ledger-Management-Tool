
import streamlit as st
import pandas as pd
from oracle_db import *

st.set_page_config("📘 Accounting Dashboard", layout="wide")

# Login/Register
if "user_id" not in st.session_state:
    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("👤 Username", key="login_user")
        password = st.text_input("🔑 Password", type="password", key="login_pass")
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    with tab2:
        new_user = st.text_input("👤 New Username", key="reg_user")
        new_pass = st.text_input("🔒 New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("✅ Registered. Please login.")
            else:
                st.error("⚠️ Username already exists.")
    st.stop()

# Sidebar navigation
st.sidebar.title("📊 Navigation")
menu = st.sidebar.radio("Go to", ["Add Journal Entry", "View Reports", "T-Ledgers", "Summary", "Export CSV", "Logout"])

# Welcome title
st.title(f"📒 Welcome, {st.session_state.username}")

# Add Journal Entry
if menu == "Add Journal Entry":
    st.subheader("➕ New Journal Entry")
    accounts = ["Cash", "Accounts Receivable", "Revenue", "Rent", "Utilities", "Accounts Payable"]

    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("📅 Date")
            desc = st.text_input("📝 Description")
        with col2:
            debit = st.selectbox("📥 Debit Account", accounts)
            debit_amt = st.number_input("💸 Debit Amount", min_value=0.01, step=0.01)
            credit = st.selectbox("📤 Credit Account", accounts)
            credit_amt = st.number_input("💵 Credit Amount", min_value=0.01, step=0.01)

        submitted = st.form_submit_button("✅ Add Entry")

    if submitted:
        if debit == credit:
            st.error("⚠️ Debit and Credit accounts must be different.")
        elif debit_amt != credit_amt:
            st.error("⚠️ Debit and Credit amounts must be equal!")
        elif debit_amt != credit_amt:
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
            st.success("✅ Transaction added successfully!")
        if debit_amt < 1.0:
           st.warning("⚠️ Amount is too small. Please verify if this is intentional.")
   

# View Reports
elif menu == "View Reports":
    st.subheader("📘 General Journal")
    df = get_user_transactions(st.session_state.user_id)

    if df.empty:
        st.info("No transactions yet.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"🧾 {row['description']} — {row['txn_date']}"):
                st.write(f"**Debit**: {row['debit_account']} — {row['debit_amount']}")
                st.write(f"**Credit**: {row['credit_account']} — {row['credit_amount']}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{row['txn_id']}"):
                        with st.form(f"form_edit_{row['txn_id']}"):
                            new_date = st.date_input("Date", value=pd.to_datetime(row['txn_date']))
                            new_desc = st.text_input("Description", row['description'])
                            new_debit = st.text_input("Debit Account", row['debit_account'])
                            new_debit_amt = st.number_input("Debit Amount", value=float(row['debit_amount']), min_value=0.01, step=0.01)
                            new_credit = st.text_input("Credit Account", row['credit_account'])
                            new_credit_amt = st.number_input("Credit Amount", value=float(row['credit_amount']), min_value=0.01, step=0.01)
                            submitted = st.form_submit_button("💾 Save Changes")

                            if submitted:
                                if new_debit == new_credit:
                                    st.error("⚠️ Debit and Credit accounts must be different.")
                                elif new_debit_amt != new_credit_amt:
                                    st.error("⚠️ Amounts must be equal.")
                                else:
                                    update_transaction(row['txn_id'], {
                                        "date": str(new_date),
                                        "description": new_desc,
                                        "debit_account": new_debit,
                                        "debit_amount": new_debit_amt,
                                        "credit_account": new_credit,
                                        "credit_amount": new_credit_amt
                                    })
                                    st.success("✅ Updated!")
                                    st.rerun()

                with col2:
                    if st.button("🗑️ Delete", key=f"del_{row['txn_id']}"):
                        delete_transaction(row['txn_id'])
                        st.success("✅ Deleted.")
                        st.rerun()

# T-Ledgers
elif menu == "T-Ledgers":
    st.subheader("📗 T-Ledgers")
    df = get_user_transactions(st.session_state.user_id)

    if 'txn_date' not in df.columns:
        df.rename(columns={'TXN_DATE': 'txn_date'}, inplace=True)

    ledgers = {}
    for _, row in df.iterrows():
        for acc, val, typ in [(row['debit_account'], row['debit_amount'], 'Debit'),
                              (row['credit_account'], row['credit_amount'], 'Credit')]:
            if acc not in ledgers:
                ledgers[acc] = []
            ledgers[acc].append({
                'Date': row['txn_date'],
                'Description': row['description'],
                'Debit': val if typ == 'Debit' else '',
                'Credit': val if typ == 'Credit' else ''
            })

    for acc, entries in ledgers.items():
        st.markdown(f"### 📂 Account: `{acc}`")
        df_ledger = pd.DataFrame(entries)
        df_ledger['Debit'] = pd.to_numeric(df_ledger['Debit'], errors='coerce').fillna(0)
        df_ledger['Credit'] = pd.to_numeric(df_ledger['Credit'], errors='coerce').fillna(0)
        df_ledger['Balance'] = df_ledger['Debit'] - df_ledger['Credit']
        df_ledger['Running Balance'] = df_ledger['Balance'].cumsum()
        st.dataframe(df_ledger, use_container_width=True)

# Summary
elif menu == "Summary":
    st.subheader("📈 Monthly Summary")
    df = get_user_transactions(st.session_state.user_id)
    df['Month'] = pd.to_datetime(df['txn_date']).dt.to_period('M')
    
    summary = df.groupby('Month').agg({
        'debit_amount': 'sum',
        'credit_amount': 'sum'
    }).reset_index()
    summary.columns = ['Month', 'Total Debits', 'Total Credits']
    summary['Net'] = summary['Total Debits'] - summary['Total Credits']
    
    st.bar_chart(summary.set_index('Month')[['Total Debits', 'Total Credits']])
    st.dataframe(summary)

# Export CSV
elif menu == "Export CSV":
    st.subheader("📦 Export Journal Entries")
    df = get_user_transactions(st.session_state.user_id)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "journal.csv", "text/csv")

# Logout
elif menu == "Logout":
    st.session_state.clear()
    st.rerun()
