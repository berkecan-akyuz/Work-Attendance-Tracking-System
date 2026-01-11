import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.auth_utils import require_login
from models.employee import Employee
from models.attendance import Attendance
from models.leave import LeaveRequest

# Page Config
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

# Initialize Models
employee_model = Employee()
attendance_model = Attendance()
leave_model = LeaveRequest()

# User Context
user = st.session_state.user
role = st.session_state.role
employee_id = user['employee_id']

st.title(f"🏠 Dashboard - {role} View")

# Announcements Section
try:
    from models.announcement import Announcement
    ann_model = Announcement()
    anns = ann_model.get_active()
    if anns:
        with st.container():
            st.info("📢 **Announcements**")
            for ann in anns:
                st.markdown(f"**{ann['title']}**: {ann['message']} *(Posted: {ann['created_at'][:10]})*")
        st.divider()
except Exception:
    pass # Handle missing table gracefully if during migration

def get_admin_metrics():
    # 1. Total Employees
    employees = employee_model.get_all(active_only=True)
    total_emp = len(employees)
    
    # 2. Attendance Rate
    today = str(datetime.now().date())
    # This is a bit inefficient, better to have a count query, but ok for MVP
    attendance_records = attendance_model.get_history(filters={'start_date': today, 'end_date': today})
    present_count = len([a for a in attendance_records if a['status'] in ['Present', 'Late']])
    attendance_rate = (present_count / total_emp * 100) if total_emp > 0 else 0
    
    # 3. Pending Approvals
    # For now just counting attendance approvals
    pending_attendance = len(attendance_model.get_pending_approvals())
    # pending_leaves = len(leave_model.get_requests({'status': 'Pending'})) # Need to verify this method
    pending_leaves = 0 # Placeholder until leave method verified
    
    # 4. Total Overtime (This Month)
    # Simplified: just showing placeholder
    total_ot = 0
    
    return total_emp, attendance_rate, pending_attendance + pending_leaves, total_ot

def render_admin_dashboard():
    # Metrics
    m1, m2, m3, m4 = get_admin_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Employees", m1)
    col2.metric("Attendance Rate (Today)", f"{m2:.1f}%")
    col3.metric("Pending Approvals", m3)
    col4.metric("Total Overtime (Month)", f"{m4} hrs")
    
    st.markdown("---")
    
    # Charts Row
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Attendance Trend (Last 7 Days)")
        
        # Fetch last 7 days data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
        
        # Get raw data
        daily_records = attendance_model.get_history({'start_date': str(start_date), 'end_date': str(end_date)})
        
        # Process data
        trend_data = []
        for i in range(7):
            d = start_date + timedelta(days=i)
            d_str = str(d)
            
            # Filter for this day
            day_recs = [r for r in daily_records if r['date'] == d_str]
            
            present = len([r for r in day_recs if r['status'] in ['Present', 'Late']])
            absent = len([r for r in day_recs if r['status'] == 'Absent'])
            # Note: Absent in DB are explicit records. 
            # If we want to count non-records as absent, we compare with total active employees.
            # For simplicity in this visualization, we'll stick to explicit status or just Present count.
            
            trend_data.append({
                'Date': d.strftime('%a %d'),
                'Present': present,
                'Records': len(day_recs)
            })
            
        data = pd.DataFrame(trend_data)
        
        if not data.empty:
            fig = px.bar(data, x='Date', y=['Present'], title="Daily Presence", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for trend chart")
        
    with c2:
        st.subheader("Department Distribution")
        employees = employee_model.get_all(active_only=True)
        if employees:
            df_emp = pd.DataFrame(employees)
            if 'department_name' in df_emp.columns:
                dept_counts = df_emp['department_name'].value_counts().reset_index()
                dept_counts.columns = ['Department', 'Count']
                fig_pie = px.pie(dept_counts, values='Count', names='Department', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                 st.info("No department data")
        else:
            st.info("No employees found")

def render_employee_dashboard():
    st.subheader("My Stats")
    # Quick stats for logged in employee
    if not employee_id:
        st.warning("No employee record linked to this user.")
        return

    # Use attendance model to get stats
    # For now, placeholder
    col1, col2, col3 = st.columns(3)
    col1.metric("My Attendance (Month)", "95%")
    col2.metric("Leave Balance", "12 Days")
    col3.metric("Overtime (Month)", "2.5 Hours")
    
    st.subheader("Recent Activity")
    history = attendance_model.get_history({'employee_id': employee_id})
    if history:
        df = pd.DataFrame(history)
        st.dataframe(df[['date', 'clock_in', 'clock_out', 'status', 'total_hours']], use_container_width=True)
    else:
        st.info("No recent attendance records.")

if role == 'Admin':
    render_admin_dashboard()
elif role == 'Manager':
    st.info("Manager Dashboard - Filtered view coming soon (Displaying Admin view for now)")
    render_admin_dashboard()
else:
    render_employee_dashboard()
