import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth_utils import require_login, render_sidebar
from models.expense import Expense
import os

st.set_page_config(page_title="Expenses", page_icon="💸", layout="wide")
require_login()
render_sidebar()

st.title("💸 Expense Reimbursements")

role = st.session_state.role
user = st.session_state.user
expense_model = Expense()

# --- Employee View: Submit Expense ---
if role == 'Employee' or role == 'Manager': # Managers also submit expenses
    st.subheader("Submit Claim")
    with st.form("expense_form"):
        c1, c2 = st.columns(2)
        date = c1.date_input("Date of Expense")
        amount = c2.number_input("Amount ($)", min_value=0.0, step=0.1)
        category = st.selectbox("Category", ["Travel", "Food", "Equipment", "Other"])
        desc = st.text_area("Description")
        receipt = st.file_uploader("Upload Receipt", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Submit Claim"):
            if amount > 0:
                receipt_path = None
                if receipt:
                    receipt_path = os.path.join("uploads", "receipts", f"{user['id']}_{int(datetime.now().timestamp())}_{receipt.name}")
                    with open(receipt_path, "wb") as f:
                        f.write(receipt.getbuffer())
                
                # Need employee ID. If user is admin/manager without linked employee, this fails.
                if user.get('employee_id'):
                    expense_model.create(user['employee_id'], str(date), amount, category, desc, receipt_path)
                    st.success("Claim Submitted!")
                    st.rerun()
                else:
                    st.error("No linked employee profile found.")
            else:
                st.error("Invalid amount")

    st.subheader("My History")
    if user.get('employee_id'):
        history = expense_model.get_by_employee(user['employee_id'])
        if history:
            st.dataframe(pd.DataFrame(history)[['date', 'category', 'amount', 'status', 'description']], use_container_width=True)
        else:
            st.info("No expense history.")

# --- Manager/Admin View: Approvals ---
if role in ['Admin', 'Manager']:
    st.divider()
    st.header("📋 Expense Approvals")
    
    pending = expense_model.get_pending()
    if pending:
        for ex in pending:
            with st.expander(f"{ex['first_name']} {ex['last_name']} - ${ex['amount']} ({ex['category']})"):
                c1, c2 = st.columns([2, 1])
                c1.write(f"**Date:** {ex['date']}")
                c1.write(f"**Reason:** {ex['description']}")
                if ex['receipt_path'] and os.path.exists(ex['receipt_path']):
                    c1.image(ex['receipt_path'], caption="Receipt", width=200) if ex['receipt_path'].endswith(('.png', '.jpg')) else c1.write("PDF Receipt attached")
                
                with c2:
                    if st.button("Approve", key=f"app_{ex['id']}"):
                        expense_model.update_status(ex['id'], 'Approved', user['id'])
                        st.success("Approved")
                        st.rerun()
                    if st.button("Reject", key=f"rej_{ex['id']}"):
                        expense_model.update_status(ex['id'], 'Rejected', user['id'])
                        st.error("Rejected")
                        st.rerun()
    else:
        st.info("No pending approvals.")
