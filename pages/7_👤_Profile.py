import streamlit as st
from utils.auth_utils import require_login
from services.auth_service import AuthService

# Page Config
st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

st.title("👤 User Profile")

auth_service = AuthService()
user = st.session_state.user

col1, col2 = st.columns([1, 2])

with col1:
    st.info(f"""
    **Username:** {user['username']}
    **Role:** {user['role']}
    **User ID:** {user['id']}
    """)
    if user['employee_id']:
        st.success("✅ Employee Account Linked")
    else:
        st.warning("⚠️ No Linked Employee Account")

with col2:
    st.subheader("Change Password")
    with st.form("change_pass"):
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Update Password"):
            if new_pass != confirm_pass:
                st.error("Passwords do not match")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters")
            else:
                auth_service.change_password(user['id'], None, new_pass)
                st.success("Password updated successfully")

# --- Document Vault ---
st.divider()
st.subheader("📂 Document Vault")

# Upload (Admin Only)
if st.session_state.role == 'Admin':
    with st.expander("Upload New Document"):
        with st.form("upload_doc"):
            d_name = st.text_input("Document Name")
            d_type = st.selectbox("Type", ["Contract", "ID", "Tax Form", "Other"])
            d_file = st.file_uploader("Upload File")
            if st.form_submit_button("Upload"):
                if d_file:
                    import os
                    from database.db_manager import DBManager
                    db = DBManager()
                    # Use unique name
                    save_path = os.path.join("uploads", "docs", f"{user['employee_id']}_{int(datetime.now().timestamp())}_{d_file.name}")
                    with open(save_path, "wb") as f:
                        f.write(d_file.getbuffer())
                    
                    # Store against the profile being VIEWED? Or currently logged in?
                    # Ideally Admin selects emp ID. But here Profile page is usually "My Profile".
                    # If this page is strictly "My Profile", Admin uploads their own docs.
                    # For Admin to upload EMP docs, need to be in Employee Management page.
                    # Assuming basic "Personal Vault" for now.
                    if user['employee_id']:
                         db.execute_query("INSERT INTO employee_documents (employee_id, name, file_path, type) VALUES (?, ?, ?, ?)", 
                                          (user['employee_id'], d_name, save_path, d_type))
                         st.success("Uploaded")
                         st.rerun()
                    else:
                        st.error("No linked employee account to store document for.")

# List Docs
if user.get('employee_id'):
    from database.db_manager import DBManager
    db = DBManager()
    docs = db.execute_query("SELECT * FROM employee_documents WHERE employee_id = ?", (user['employee_id'],), fetch_all=True)
    
    if docs:
        for d in docs:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"📄 **{d['name']}** ({d['type']})")
            with c2:
                with open(d['file_path'], "rb") as f:
                    st.download_button("Download", f, file_name=os.path.basename(d['file_path']), key=f"dl_{d['id']}")
    else:
        st.info("No documents found.")
