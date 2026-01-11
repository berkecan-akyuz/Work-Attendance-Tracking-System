import streamlit as st
import pandas as pd
from utils.auth_utils import require_login, check_role
from models.settings import SettingsModel
from models.user import User

# Page Config
st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

check_role(['Admin'])

st.title("⚙️ System Settings")

settings_model = SettingsModel()
# user_model removed as moved to separate page

tabs = ["System Config", "Departments", "Leave Types", "Public Holidays", "Branding", "Shifts"]
selected_tab = st.radio("Navigation", tabs, horizontal=True)

if selected_tab == "System Config":
    st.subheader("General Configuration")
    settings = settings_model.get_system_settings()
    
    # Needs efficient way to edit. For now, simple list
    for s in settings:
        with st.form(f"setting_{s['key']}"):
            val = st.text_input(f"{s['description']} ({s['key']})", value=s['value'])
            if st.form_submit_button("Update"):
                settings_model.update_setting(s['key'], val)
                st.success("Updated")
                st.rerun()

elif selected_tab == "Public Holidays":
    from models.holidays import Holiday
    from datetime import datetime
    
    holiday_model = Holiday()
    st.subheader("Public Holidays")
    
    with st.form("add_holiday"):
        c1, c2 = st.columns(2)
        h_name = c1.text_input("Holiday Name")
        h_date = c2.date_input("Date")
        
        if st.form_submit_button("Add Holiday"):
            if h_name:
                try:
                    holiday_model.add(str(h_date), h_name, h_date.year)
                    st.success("Added")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error (maybe duplicate): {e}")
            else:
                st.error("Name required")
                
    # List Holidays
    holidays = holiday_model.get_all(datetime.now().year)
    if holidays:
        st.write(f"Holidays for {datetime.now().year}")
        st.dataframe(pd.DataFrame(holidays)[['date', 'name']], use_container_width=True)
        
        # Deletion
        h_to_del = st.selectbox("Select to Delete", options=holidays, format_func=lambda x: f"{x['date']} - {x['name']}")
        if st.button("Delete Selected"):
            holiday_model.delete(h_to_del['id'])
            st.success("Deleted")
            st.rerun()

elif selected_tab == "Branding":
    st.subheader("Branding & Personalization")
    st.info("Upload your company logo to appear in the sidebar.")
    
    current_logo = settings_model.db.execute_query("SELECT value FROM system_settings WHERE key = 'company_logo'", fetch_one=True)
    
    if current_logo:
        st.image(current_logo['value'], width=200, caption="Current Logo")
        
    uploaded_logo = st.file_uploader("Upload New Logo", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_logo:
        import os
        save_path = os.path.join("assets", "logo.png") # Fixed name for simplicity
        os.makedirs("assets", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
            
        # Update setting
        existing = settings_model.db.execute_query("SELECT id FROM system_settings WHERE key = 'company_logo'", fetch_one=True)
        if existing:
            settings_model.update_setting('company_logo', save_path)
        else:
             settings_model.db.execute_query("INSERT INTO system_settings (key, value, description) VALUES (?, ?, ?)", 
                                             ('company_logo', save_path, 'Company Logo Path'))
        
        st.success("Logo updated! Refresh to see changes.")
        st.rerun()

elif selected_tab == "Shifts":
    from models.shift import Shift
    shift_model = Shift()
    
    st.subheader("Shift Management")
    
    with st.form("add_shift"):
        c1, c2, c3, c4 = st.columns(4)
        s_name = c1.text_input("Shift Name (e.g. Morning)")
        s_start = c2.time_input("Start Time")
        s_end = c3.time_input("End Time")
        s_grace = c4.number_input("Grace Period (mins)", value=15)
        
        if st.form_submit_button("Add Shift"):
            if s_name:
                shift_model.create(s_name, str(s_start), str(s_end), s_grace)
                st.success("Shift Added")
                st.rerun()
                
    shifts = shift_model.get_all()
    if shifts:
        st.dataframe(pd.DataFrame(shifts), use_container_width=True)

elif selected_tab == "Departments":
    st.subheader("Department Management")
    
    with st.form("add_dept"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("New Department Name")
        desc = c2.text_input("Description")
        budget = c3.number_input("Monthly Budget ($)", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("Add Department"):
            if name:
                # Direct SQL for budget column support if model isn't updated
                try:
                    settings_model.db.execute_query("INSERT INTO departments (name, description, budget) VALUES (?, ?, ?)", (name, desc, budget))
                    st.success("Added")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    depts = settings_model.get_departments()
    if depts:
        # Custom list with budget editing
        for d in depts:
            with st.expander(f"{d['name']}"):
                col_a, col_b = st.columns(2)
                col_a.write(d.get('description', ''))
                curr_bud = float(d.get('budget') or 0)
                new_bud = col_b.number_input(f"Budget for {d['name']}", value=curr_bud, key=f"bud_{d['id']}")
                if col_b.button("Update Budget", key=f"upd_{d['id']}"):
                    settings_model.db.execute_query("UPDATE departments SET budget = ? WHERE id = ?", (new_bud, d['id']))
                    st.success("Updated!")
                    st.rerun()

elif selected_tab == "Leave Types":
    st.subheader("Leave Type Configuration")
    
    with st.form("add_leave_type"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Type Name")
        days = c2.number_input("Days Allowed", min_value=0, value=10)
        is_paid = c3.checkbox("Is Paid?", value=True)
        
        if st.form_submit_button("Add Leave Type"):
            if name:
                settings_model.create_leave_type(name, days, is_paid)
                st.success("Added")
                st.rerun()
                
    lts = settings_model.get_leave_types()
    if lts:
        st.dataframe(pd.DataFrame(lts), use_container_width=True)
    st.subheader("General Configuration")
    settings = settings_model.get_system_settings()
    
    # Needs efficient way to edit. For now, simple list
    for s in settings:
        with st.form(f"setting_{s['key']}"):
            val = st.text_input(f"{s['description']} ({s['key']})", value=s['value'])
            if st.form_submit_button("Update"):
                settings_model.update_setting(s['key'], val)
                st.success("Updated")
                st.rerun()

elif selected_tab == "Public Holidays":
    from models.holidays import Holiday
    from datetime import datetime
    
    holiday_model = Holiday()
    st.subheader("Public Holidays")
    
    with st.form("add_holiday"):
        c1, c2 = st.columns(2)
        h_name = c1.text_input("Holiday Name")
        h_date = c2.date_input("Date")
        
        if st.form_submit_button("Add Holiday"):
            if h_name:
                try:
                    holiday_model.add(str(h_date), h_name, h_date.year)
                    st.success("Added")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error (maybe duplicate): {e}")
            else:
                st.error("Name required")
                
    # List Holidays
    holidays = holiday_model.get_all(datetime.now().year)
    if holidays:
        st.write(f"Holidays for {datetime.now().year}")
        st.dataframe(pd.DataFrame(holidays)[['date', 'name']], use_container_width=True)
        
        # Deletion
        h_to_del = st.selectbox("Select to Delete", options=holidays, format_func=lambda x: f"{x['date']} - {x['name']}")
        if st.button("Delete Selected"):
            holiday_model.delete(h_to_del['id'])
            st.success("Deleted")
            st.rerun()

elif selected_tab == "Branding":
    st.subheader("Branding & Personalization")
    st.info("Upload your company logo to appear in the sidebar.")
    
    current_logo = settings_model.db.execute_query("SELECT value FROM system_settings WHERE key = 'company_logo'", fetch_one=True)
    
    if current_logo:
        st.image(current_logo['value'], width=200, caption="Current Logo")
        
    uploaded_logo = st.file_uploader("Upload New Logo", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_logo:
        import os
        save_path = os.path.join("assets", "logo.png") # Fixed name for simplicity
        os.makedirs("assets", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
            
        # Update setting
        existing = settings_model.db.execute_query("SELECT id FROM system_settings WHERE key = 'company_logo'", fetch_one=True)
        if existing:
            settings_model.update_setting('company_logo', save_path)
        else:
             settings_model.db.execute_query("INSERT INTO system_settings (key, value, description) VALUES (?, ?, ?)", 
                                             ('company_logo', save_path, 'Company Logo Path'))
        
        st.success("Logo updated! Refresh to see changes.")
        st.rerun()

elif selected_tab == "Shifts":
    from models.shift import Shift
    shift_model = Shift()
    
    st.subheader("Shift Management")
    
    with st.form("add_shift"):
        c1, c2, c3, c4 = st.columns(4)
        s_name = c1.text_input("Shift Name (e.g. Morning)")
        s_start = c2.time_input("Start Time")
        s_end = c3.time_input("End Time")
        s_grace = c4.number_input("Grace Period (mins)", value=15)
        
        if st.form_submit_button("Add Shift"):
            if s_name:
                shift_model.create(s_name, str(s_start), str(s_end), s_grace)
                st.success("Shift Added")
                st.rerun()
                
    shifts = shift_model.get_all()
    if shifts:
        st.dataframe(pd.DataFrame(shifts), use_container_width=True)

elif selected_tab == "Audit Logs":
    from models.audit import AuditLog
    audit = AuditLog()
    st.subheader("🛡️ Security Audit Logs")
    
    logs = audit.get_logs(limit=200)
    
    if logs:
        df = pd.DataFrame(logs)
        # Format details
        df['User'] = df.apply(lambda x: f"{x['username']} ({x['first_name']} {x['last_name']})" if x['username'] else "System", axis=1)
        
        # Filters
        c1, c2 = st.columns(2)
        search_action = c1.text_input("Filter by Action (e.g. UPDATE, DELETE)")
        search_table = c2.text_input("Filter by Table (e.g. employees)")
        
        if search_action:
            df = df[df['action'].str.contains(search_action, case=False, na=False)]
        if search_table:
            df = df[df['target_table'].str.contains(search_table, case=False, na=False)]
            
        st.dataframe(
            df[['timestamp', 'User', 'action', 'target_table', 'target_id', 'details']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No logs found.")



elif selected_tab == "Announcements":
    from models.announcement import Announcement
    ann_model = Announcement()
    
    st.header("📢 Manage Announcements")
    
    with st.expander("Create New Announcement", expanded=True):
        with st.form("new_announcement"):
            title = st.text_input("Title")
            message = st.text_area("Message")
            if st.form_submit_button("Post Announcement"):
                if title and message:
                    ann_model.create(title, message)
                    st.success("Posted!")
                    st.rerun()
                else:
                    st.error("Title and Message required.")
    
    st.subheader("History")
    anns = ann_model.get_all()
    if anns:
        for ann in anns:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.info(f"**{ann['title']}**\n\n{ann['message']}\n\n*Posted: {ann['created_at']}*")
            with c2:
                if st.button("Delete", key=f"del_ann_{ann['id']}"):
                    ann_model.delete(ann['id'])
                    st.rerun()

elif selected_tab == "Departments":
    st.subheader("Department Management")
    
    with st.form("add_dept"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("New Department Name")
        desc = c2.text_input("Description")
        budget = c3.number_input("Monthly Budget ($)", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("Add Department"):
            if name:
                # Direct SQL for budget column support if model isn't updated
                try:
                    settings_model.db.execute_query("INSERT INTO departments (name, description, budget) VALUES (?, ?, ?)", (name, desc, budget))
                    st.success("Added")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    depts = settings_model.get_departments()
    if depts:
        #df = pd.DataFrame(depts)
        #st.dataframe(df[['id', 'name', 'description']], use_container_width=True)
        # Custom list with budget editing
        for d in depts:
            with st.expander(f"{d['name']}"):
                col_a, col_b = st.columns(2)
                col_a.write(d.get('description', ''))
                curr_bud = float(d.get('budget') or 0)
                new_bud = col_b.number_input(f"Budget for {d['name']}", value=curr_bud, key=f"bud_{d['id']}")
                if col_b.button("Update Budget", key=f"upd_{d['id']}"):
                    settings_model.db.execute_query("UPDATE departments SET budget = ? WHERE id = ?", (new_bud, d['id']))
                    st.success("Updated!")
                    st.rerun()

elif selected_tab == "Leave Types":
    st.subheader("Leave Type Configuration")
    
    with st.form("add_leave_type"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Type Name")
        days = c2.number_input("Days Allowed", min_value=0, value=10)
        is_paid = c3.checkbox("Is Paid?", value=True)
        
        if st.form_submit_button("Add Leave Type"):
            if name:
                settings_model.create_leave_type(name, days, is_paid)
                st.success("Added")
                st.rerun()
                
    lts = settings_model.get_leave_types()
    if lts:
        st.dataframe(pd.DataFrame(lts), use_container_width=True)

elif selected_tab == "User Management":
    st.subheader("User Management")
    
    with st.form("create_user"):
        st.write("Create New User")
        c1, c2, c3 = st.columns(3)
        u_name = c1.text_input("Username")
        u_pass = c2.text_input("Password", type="password")
        u_role = c3.selectbox("Role", ["Employee", "Manager", "Admin"])
        u_emp_id = st.number_input("Employee ID (Optional)", value=0)
        
        if st.form_submit_button("Create User"):
            if u_name and u_pass:
                # Need auth service strictly for creating user to handle hashing properly if not using model directly
                # Model handles hashing if implemented there? 
                # Our User.create_user handles hashing.
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
