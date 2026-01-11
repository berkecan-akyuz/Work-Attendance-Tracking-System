import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.auth_utils import require_login, check_role
from models.attendance import Attendance
from models.employee import Employee
from models.leave import LeaveRequest
import io

# Page Config
st.set_page_config(page_title="Reports", page_icon="📊", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

check_role(['Admin', 'Manager'])

st.title("📊 Reports & Analytics")

attendance_model = Attendance()
employee_model = Employee()
leave_model = LeaveRequest()

# Tabs
tabs = ["Daily Report", "Monthly Report", "Overtime Report", "Advanced Analytics"]
selected_tab = st.radio("Report Type", tabs, horizontal=True)

# Helper for standard reports
def get_date_range():
    col1, col2 = st.columns(2)
    s = col1.date_input("Start Date", value=datetime.now().replace(day=1))
    e = col2.date_input("End Date", value=datetime.now())
    return s, e

if selected_tab in ["Daily Report", "Monthly Report", "Overtime Report"]:
    
    start_date, end_date = get_date_range()
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating..."):
            raw_data = attendance_model.get_history({'start_date': str(start_date), 'end_date': str(end_date)})
            
            if raw_data:
                df = pd.DataFrame(raw_data)
                
                if selected_tab == "Daily Report":
                    st.dataframe(df[['date', 'first_name', 'last_name', 'department_name', 'status', 'clock_in', 'clock_out', 'total_hours']], use_container_width=True)
                    
                elif selected_tab == "Monthly Summary":
                    summary = df.groupby(['employee_id', 'first_name', 'last_name', 'department_name']).agg(
                        Days=('date', 'count'),
                        Hours=('total_hours', 'sum'),
                        OT=('overtime_hours', 'sum')
                    ).reset_index()
                    st.dataframe(summary, use_container_width=True)
                    
                    fig = px.bar(summary, x='first_name', y='Hours', title='Total Hours by Employee')
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif selected_tab == "Overtime Report":
                    ot_summary = df.groupby(['department_name'])['overtime_hours'].sum().reset_index()
                    st.dataframe(ot_summary, use_container_width=True)
                    
                    fig_ot = px.pie(ot_summary, values='overtime_hours', names='department_name', title='Overtime Share by Department')
                    st.plotly_chart(fig_ot, use_container_width=True)

            else:
                st.info("No records found.")

elif selected_tab == "Advanced Analytics":
    st.subheader("📈 Workforce Insights (Last 30 Days)")
    
    # Needs data: All attendance records with dept info
    from database.db_manager import DBManager
    db = DBManager()
    
    # 30 day Lookback
    query = """
    SELECT a.*, e.first_name, e.last_name, d.name as dept_name
    FROM attendance a
    JOIN employees e ON a.employee_id = e.id
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE a.date >= date('now', '-30 days')
    """
    data = db.execute_query(query, fetch_all=True)
    
    if data:
        df = pd.DataFrame(data)
        
        # Row 1: Overtime & Lateness
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🏢 Overtime by Department")
            if 'overtime_hours' in df.columns:
                ot_by_dept = df.groupby('dept_name')['overtime_hours'].sum().reset_index()
                fig_ot = px.bar(ot_by_dept, x='dept_name', y='overtime_hours', color='dept_name')
                st.plotly_chart(fig_ot, use_container_width=True)
            else:
                st.warning("No overtime data.")
                
        with c2:
            st.markdown("##### 📉 Lateness Trend")
            # Assume 'Late' status exists or we strictly check time. 
            # Ideally we have 'status' column. If not, we might need to rely on business logic.
            # Assuming 'status' column is present from get_history query or raw table if updated.
            # Let's check status distribution
            status_trend = df.groupby(['date', 'status']).size().reset_index(name='count')
            if not status_trend.empty:
               fig_trend = px.line(status_trend, x='date', y='count', color='status', markers=True)
               st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No status trend data available.")

        # Row 2: Day of Week
        st.markdown("##### 📅 Lateness by Day of Week")
        df['date_obj'] = pd.to_datetime(df['date'])
        df['day_name'] = df['date_obj'].dt.day_name()
        
        late_only = df[df['status'] == 'Late']
        if not late_only.empty:
            dow_counts = late_only['day_name'].value_counts().reindex(
                ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            ).fillna(0).reset_index()
            dow_counts.columns = ['Day', 'Late Count']
            
            fig_dow = px.bar(dow_counts, x='Day', y='Late Count', color='Late Count', color_continuous_scale='Reds')
            st.plotly_chart(fig_dow, use_container_width=True)
        else:
            st.success("No lateness recorded in the last 30 days!")

    else:
        st.info("No sufficient data for analytics.")
