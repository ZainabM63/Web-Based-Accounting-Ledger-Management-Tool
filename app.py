import streamlit as st
import pandas as pd
from oracle_db import (
    login_user,
    register_user,
    add_transaction,
    get_user_transactions
)

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="📘 Accounting Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ENHANCED CSS (UI FIXES)
# =========================
st.markdown("""
<style>
/* Remove white gaps at the top and bottom */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
    max-width: 95% !important;
}

/* Fix background and hide Streamlit branding */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f8fafc, #e2e8f0);
}

header[data-testid="stHeader"], footer {
    display: none !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
}
section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
    color: #f1f5f9 !important;
}

/* Modern Card Design */
.card {
    background: white;
    padding: 24px;
    border-radius: 15px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    border: 1px solid #e2e8f0;
    margin-bottom: 10px;
}

/* Styled Form Container to replace the empty white bars */
.form-container {
    background: #ffffff;
    padding: 30px;
    border-radius: 20px;
    border: 1px solid #dee2e6;
}

/* Button Customization */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #2563eb;
    color: white;
    border: none;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #1e40af;
    border: none;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =========================
if "user_id" not in st.session_state:
    # Adding a clean header with a slight top margin
    st.markdown("""
        <div style='text-align:center; margin-top:60px; margin-bottom:20px;'>
            <h1 style='color:#1e293b; font-size: 42px; margin-bottom:0;'>📘 Accounting Dashboard</h1>
            <p style='color:#64748b; font-size: 18px;'>Secure • Accurate • Double-Entry Ledger</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.4, 1])
    
    with col2:
        # We wrap the tabs in a container to match the card width
        tab1, tab2 = st.tabs(["🔐 Login", "🆕 Create New Account"])
        
        with tab1:
            # We use your 'card' class for consistency
            st.markdown("<div class='card' style='margin-top:-10px; border-top-left-radius:0; border-top-right-radius:0;'>", unsafe_allow_html=True)
            
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign In"):
                uid = login_user(username, password)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='card' style='margin-top:-10px; border-top-left-radius:0; border-top-right-radius:0;'>", unsafe_allow_html=True)
            
            new_user = st.text_input("New Username", key="reg_user", placeholder="Choose a username")
            new_pass = st.text_input("New Password", type="password", key="reg_pass", placeholder="Create a strong password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Register Account"):
                if register_user(new_user, new_pass):
                    st.success("✅ Account created! Switch to the Login tab.")
                else:
                    st.warning("⚠️ This username is already taken.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
    st.stop()
# =========================
# HEADER SECTION
# =========================
# Using a single clean div to prevent double bars
st.markdown(f"""
<div class="card" style="display:flex; align-items:center; gap:20px; border-left: 8px solid #2563eb;">
    <div style="font-size:45px;">📘</div>
    <div>
        <h2 style="margin:0; color:#1e293b;">Accounting Dashboard</h2>
        <p style="margin:0; color:#64748b; font-weight:500;">Welcome back, {st.session_state.username} | {pd.Timestamp.now().strftime('%Y-%m-%d')}</p>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* 1. Force Sidebar background and white text for all elements */
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
}

/* 2. Target the radio button labels (Menu items) specifically to be white */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] label p {
    color: white !important;
    font-weight: 500 !important;
}

/* 3. Ensure the Navigation header and caption are also white */
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] .stCaption p {
    color: white !important;
}

/* 4. Remove default padding at the bottom of the sidebar to help push text down */
[data-testid="stSidebarUserContent"] {
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Sidebar Logic
# =========================
st.sidebar.markdown("### 📊 Navigation")
menu = st.sidebar.radio(
    "Go To:",
    ["➕ Add Journal Entry", "📘 View Reports", "📗 T-Ledgers", "📦 Export CSV", "❓ Help", "🚪 Logout"],
    label_visibility="collapsed"
)

# This creates flexible empty space to push the caption to the bottom
st.sidebar.container(height=400, border=False) 

st.sidebar.divider()
st.sidebar.caption("© 2026 Accounting Dashboard")
# =========================
# DASHBOARD CONTENT
# =========================

if menu == "➕ Add Journal Entry":
    st.markdown("<div class='card'><h3>➕ New Journal Entry</h3>", unsafe_allow_html=True)
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Transaction Date")
            desc = st.text_input("Description", placeholder="e.g., Office Supplies")
            debit_acc = st.text_input("Debit Account")
        with c2:
            debit_amt = st.number_input("Debit Amount", min_value=0.0, step=0.01)
            credit_acc = st.text_input("Credit Account")
            credit_amt = st.number_input("Credit Amount", min_value=0.0, step=0.01)
        
        submitted = st.form_submit_button("Post Transaction")
        
        if submitted:
            if debit_amt != credit_amt:
                st.error("Balance Error: Debit must equal Credit.")
            elif not debit_acc or not credit_acc:
                st.error("Account names cannot be empty.")
            else:
                add_transaction(st.session_state.user_id, {
                    "date": str(date), "description": desc,
                    "debit_account": debit_acc, "debit_amount": debit_amt,
                    "credit_account": credit_acc, "credit_amount": credit_amt
                })
                st.success("Entry Posted Successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📘 View Reports":
    st.markdown("<div class='card'><h3>📘 General Journal</h3>", unsafe_allow_html=True)
    df = get_user_transactions(st.session_state.user_id)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No records found.")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📗 T-Ledgers":
    st.markdown("<h3>📗 Ledger Accounts</h3>", unsafe_allow_html=True)
    df = get_user_transactions(st.session_state.user_id)
    if df.empty:
        st.info("No transactions to display.")
    else:
        # Simple Ledger Logic
        accounts = set(df['debit_account']).union(set(df['credit_account']))
        for acc in accounts:
            with st.expander(f"📖 Account: {acc}", expanded=True):
                # Filter for this specific account
                d_df = df[df['debit_account'] == acc][['txn_date', 'description', 'debit_amount']]
                c_df = df[df['credit_account'] == acc][['txn_date', 'description', 'credit_amount']]
                st.write("Debits:")
                st.table(d_df)
                st.write("Credits:")
                st.table(c_df)

elif menu == "📦 Export CSV":
    st.markdown("<div class='card'><h3>📦 Data Export</h3>", unsafe_allow_html=True)
    df = get_user_transactions(st.session_state.user_id)
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download General Journal CSV", data=csv, file_name="journal.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)
elif menu == "❓ Help":
    st.markdown("""
    <div class='card'>
        <h2 style='color: #2563eb;'>❓ System Support & Guide</h2>
        <hr>
        <div style='display: flex; gap: 20px; margin-top: 15px;'>
            <div style='flex: 1;'>
                <h4>📖 Quick Start Guide</h4>
                <ul>
                    <li><b>Journal Entries:</b> Use the 'Add Entry' tab to record daily transactions. Remember: Total Debits must always equal Total Credits.</li>
                    <li><b>Reporting:</b> View the 'View Reports' section for a full chronological history of your ledger.</li>
                    <li><b>T-Ledgers:</b> Automated grouping by account to help you see balances at a glance.</li>
                </ul>
            </div>
            <div style='flex: 1; border-left: 1px solid #eee; padding-left: 20px;'>
                <h4>🛠 Technical Support</h4>
                <p>If you encounter database errors or layout issues, please reach out via the contact details below.</p>
                <p><b>Developer:</b> Zainab</p>
                <p><b>Support Email:</b> <a href='mailto:zainabmughal5432@gmail.com'>zainabmughal5432@gmail.com</a></p>
                <div style='background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;'>
                    <small>💡 <b>Pro Tip:</b> Use the 'Export CSV' feature weekly to keep a local backup of your financial data.</small>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
elif menu == "🚪 Logout":
    st.session_state.clear()
    st.rerun()