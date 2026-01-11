import streamlit as st
import pandas as pd
from utils.auth_utils import require_login, check_role, render_sidebar
from models.user import User

st.set_page_config(page_title="User Management", page_icon="👤", layout="wide")
require_login()
render_sidebar()
check_role(['Admin'])

st.title("👤 User Management")

user_model = User()

with st.form("create_user"):
    st.write("Create New User")
    c1, c2, c3 = st.columns(3)
    u_name = c1.text_input("Username")
    u_pass = c2.text_input("Password", type="password")
    u_role = c3.selectbox("Role", ["Employee", "Manager", "Admin"])
    u_emp_id = st.number_input("Employee ID (Optional)", value=0)
    
    if st.form_submit_button("Create User"):
        if u_name and u_pass:
            try:
                user_model.create_user(u_name, u_pass, u_role, u_emp_id if u_emp_id > 0 else None)
                st.success("User created")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Username and Password required")
            
users = user_model.get_all_users()
if users:
    st.dataframe(pd.DataFrame(users)[['id', 'username', 'role', 'first_name', 'last_name', 'last_login']], use_container_width=True)
