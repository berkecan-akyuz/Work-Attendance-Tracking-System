import streamlit as st
from datetime import datetime
from services.attendance_service import AttendanceService
from models.employee import Employee
from utils.auth_utils import render_sidebar # Still needed? Kiosk usually hides this
import time

# Page Config
st.set_page_config(page_title="Kiosk Clock-In", page_icon="📱", layout="centered", initial_sidebar_state="collapsed")

# Kiosk specific CSS to hide things
<style>
    [data-testid="stSidebar"] {display: none;}
    /* Hide anchors - Aggressive */
    a.anchor-link { display: none !important; visibility: hidden !important; }
    [data-testid="stMarkdownContainer"] a[href^="#"] { display: none !important; }
    
    /* Removed forced background colors to match system theme */
</style>
""", unsafe_allow_html=True)

att_service = AttendanceService()
emp_model = Employee()

with st.container():
    st.title("📱 Work Attendance Kiosk")
    st.write(f"**{datetime.now().strftime('%A, %d %B %Y')}**")
    st.header(datetime.now().strftime("%H:%M"))
    
    st.divider()
    
    pin = st.text_input("Enter Employee PIN", type="password", max_chars=6)
    
    c1, c2 = st.columns(2)
    
    if c1.button("🟢 Clock In", type="primary", use_container_width=True):
        if not pin:
            st.error("PIN Required")
        else:
            emp = emp_model.db.execute_query("SELECT id, first_name, last_name FROM employees WHERE pin_code = ?", (pin,), fetch_one=True)
            if emp:
                success, msg = att_service.clock_in(emp['id'])
                if success:
                    st.success(f"Welcome, {emp['first_name']}! {msg}")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning(msg)
            else:
                st.error("Invalid PIN")

    if c2.button("🔴 Clock Out", type="secondary", use_container_width=True):
        if not pin:
            st.error("PIN Required")
        else:
            emp = emp_model.db.execute_query("SELECT id, first_name FROM employees WHERE pin_code = ?", (pin,), fetch_one=True)
            if emp:
                success, msg = att_service.clock_out(emp['id'])
                if success:
                    st.success(f"Goodbye, {emp['first_name']}! {msg}")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning(msg)
            else:
                st.error("Invalid PIN")
                
    st.caption("Use your assigned 4-6 digit PIN to record attendance.")

# Add simple "login" link to get back
st.divider()
if st.button("🔁 Switch to Standard Mode", use_container_width=True):
    st.switch_page("app.py")
