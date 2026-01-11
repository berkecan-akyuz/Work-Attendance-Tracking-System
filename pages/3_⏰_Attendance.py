import streamlit as st
import pandas as pd
from datetime import datetime, time
from utils.auth_utils import require_login, check_role
from services.attendance_service import AttendanceService
from models.employee import Employee
from models.attendance import Attendance

# Page Config
st.set_page_config(page_title="Attendance", page_icon="⏰", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

try:
    from streamlit_calendar import calendar
except ImportError:
    calendar = None
    st.error("Please install streamlit-calendar")
    
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None

attendance_service = AttendanceService()
attendance_model = Attendance()
employee_model = Employee()
user = st.session_state.user
role = st.session_state.role

st.title("⏰ Attendance Management")

# --- Quick Clock In/Out ---
st.markdown("### Quick Actions")
col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
current_emp_id = user['employee_id']

if current_emp_id:
    # Check current status
    today_record = attendance_service.get_employee_today(current_emp_id)
    clocked_in = today_record and today_record['clock_in'] and not today_record['clock_out']
    
    # Define 'today' and 'todays_record' for the new logic
    today = datetime.now().date()
    todays_record = today_record # Use the existing today_record variable

    with col1:
        st.subheader(f"👋 {user['first_name']} {user['last_name']}")
        st.write(f"**Date:** {today.strftime('%A, %d %B %Y')}") # Format date for display
        
        # Geolocation
        location = None
        if get_geolocation:
            loc = get_geolocation()
            if loc:
                location = (loc['coords']['latitude'], loc['coords']['longitude'])
                st.caption(f"📍 Location detected: {location}")
        
        if todays_record:
            st.info(f"✅ Clocked In at {datetime.fromisoformat(todays_record['clock_in']).strftime('%H:%M')}")
            if todays_record['clock_out']:
                st.success(f"Running Total: {todays_record['total_hours']:.2f} hrs")
            else:
                if st.button("Clock Out", type="primary"):
                    success, msg = attendance_service.clock_out(current_emp_id) # Use current_emp_id
                    if success:
                        st.success("Clocked Out!")
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            if st.button("Clock In", type="primary"):
                success, msg = attendance_service.clock_in(current_emp_id, location=location) # Use current_emp_id
                if success:
                    st.success("Clocked In!")
                    st.rerun()
                else:
                    st.error(msg)

    # The original col2, col3, col4 logic is replaced by the new col1 logic above.
    # Keeping col3 for current date display if the new logic doesn't fully replace it,
    # but the instruction implies a full replacement of the quick actions.
    # Given the instruction, the original col1, col2, col3, col4 structure is likely being replaced
    # or significantly altered by the new block.
    # The instruction snippet is a bit ambiguous on how to merge the old col1/col2 with the new c1.
    # I will assume the new block is intended to replace the *content* of the quick actions.
    # The instruction provided a partial snippet that seems to be a new quick action block.
    # I will replace the original quick action logic with the new one, adapting it to the existing variables.
    # The original col3 and col4 are not explicitly mentioned in the replacement, so I'll remove them
    # as the new block seems to be a self-contained quick action.

else:
    st.warning("No employee record linked. Cannot use Quick Actions.")

st.markdown("---")

# --- Tabs ---
tabs = []
if role in ['Admin', 'Manager']:
    tabs = ["Today's Overview", "Manual Entry", "History", "Shift Schedule"]
else:
    tabs = ["Today's Overview", "Calendar View", "My History", "Shift Schedule"] 
selected_tab = st.radio("Navigation", tabs, horizontal=True)

if selected_tab == "Shift Schedule":
    st.header("📅 Team Shift Schedule")
    # Visualization of shifts
    from models.employee import Employee
    emp_model = Employee()
    active_emps = emp_model.get_all(active_only=True)
    
    calendar_events = []
    
    today = datetime.now()
    # Generate mock events for this month based on assigned shift
    for e in active_emps:
        if e.get('shift_id'):
            # Just showing they are scheduled.
            calendar_events.append({
                "title": f"{e['first_name']} ({e.get('department_name', 'Gen')})",
                "start": today.strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d"),
                "resourceId": e['id'],
                "backgroundColor": "#6f42c1"
            })
            
    if calendar:
        calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
    else:
        st.warning("Calendar component not available.")

if selected_tab == "Calendar View":
    st.subheader("Attendance Calendar")
    
    # Fetch all records for user
    # Use current_emp_id for employee_id
    all_recs = attendance_model.get_history({'employee_id': current_emp_id})
    events = []
    
    status_colors = {
        'Present': '#28a745',
        'Late': '#ffc107',
        'Absent': '#dc3545',
        'On Leave': '#17a2b8'
    }
    
    for rec in all_recs:
        color = status_colors.get(rec['status'], '#6c757d')
        events.append({
            "title": f"{rec['status']} ({rec['total_hours']:.2f}h)", # Format total_hours
            "start": rec['date'],
            "allDay": True,
            "backgroundColor": color,
            "borderColor": color
        })
        
    # Also add Holidays
    from models.holidays import Holiday
    holidays = Holiday().get_all(year=datetime.now().year)
    if holidays:
        for h in holidays:
            events.append({
                "title": f"🎉 {h['name']}",
                "start": h['date'],
                "allDay": True,
                "display": "background",
                "backgroundColor": "#ffeb3b"
            })

    if calendar:
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay",
            },
            "initialView": "dayGridMonth",
        }
        calendar(events=events, options=calendar_options)

elif selected_tab == "Today's Overview":
    st.subheader("Today's Attendance Overview")
    date_str = str(datetime.now().date())
    
    # Fetch all employees
    employees = employee_model.get_all(active_only=True)
    today_records = attendance_model.get_history({'start_date': date_str, 'end_date': date_str})
    
    # Merge data
    data = []
    for emp in employees:
        record = next((r for r in today_records if r['employee_id'] == emp['id']), None)
        status = record['status'] if record else "Absent" # Default absent if no record by now (simplified)
        clock_in = record['clock_in'].split(' ')[1][:5] if record and record['clock_in'] else "-"
        clock_out = record['clock_out'].split(' ')[1][:5] if record and record['clock_out'] else "-"
        hours = f"{record['total_hours']:.2f}" if record and record['total_hours'] else "0.00"
        
        data.append({
            'Employee': f"{emp['first_name']} {emp['last_name']}",
            'Department': emp['department_name'],
            'Status': status,
            'Clock In': clock_in,
            'Clock Out': clock_out,
            'Hours': hours
        })
        
    df = pd.DataFrame(data)
    
    # Coloring Status (simplified via st.dataframe)
    st.dataframe(df, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Present", len([d for d in data if d['Status'] in ['Present', 'Late']]))
    c2.metric("Late", len([d for d in data if d['Status'] == 'Late']))
    c3.metric("Absent", len([d for d in data if d['Status'] == 'Absent']))


elif selected_tab == "Manual Entry":
    st.subheader("Manual Attendance Entry")
    
    with st.form("manual_attendance"):
        employees = employee_model.get_all(active_only=True)
        emp_options = {e['id']: f"{e['first_name']} {e['last_name']} ({e['employee_code']})" for e in employees}
        
        selected_emp_id = st.selectbox("Select Employee", options=list(emp_options.keys()), format_func=lambda x: emp_options[x])
        date = st.date_input("Date", value=datetime.now())
        
        c1, c2 = st.columns(2)
        with c1:
            in_time = st.time_input("Clock In", value=time(9, 0))
        with c2:
            out_time = st.time_input("Clock Out", value=time(17, 0))
            
        status = st.selectbox("Status", ["Present", "Late", "Half Day", "Absent"])
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Save Record"):
            # Construct datetime
            dt_in = datetime.combine(date, in_time)
            dt_out = datetime.combine(date, out_time)
            
            # Simple manual calculation override
             # Using creating record logic
            # Check if record exists
            existing_record = attendance_model.get_todays_record(selected_emp_id, str(date))

            data = {
                'employee_id': selected_emp_id,
                'date': str(date),
                'clock_in': dt_in,
                'clock_out': dt_out,
                'status': status,
                'work_type': 'Regular',
                'notes': notes
            }
            
            try:
                if existing_record:
                    # Update existing
                    # Remove fields that shouldn't change generally or just overwrite?
                    # For manual entry override, we overwrite.
                    attendance_model.update_record(existing_record['id'], data)
                    st.success(f"Attendance record for {date} updated successfully.")
                else:
                    # Create new
                    attendance_model.create_record(data)
                    st.success(f"Attendance record for {date} created successfully.")
                
            except Exception as e:
                st.error(f"Error saving record: {e}")

elif selected_tab == "History" or selected_tab == "My History":
    st.subheader("Attendance History")
    
    c1, c2 = st.columns(2)
    start_d = c1.date_input("Start Date", value=datetime.now().replace(day=1))
    end_d = c2.date_input("End Date", value=datetime.now())
    
    filters = {
        'start_date': str(start_d),
        'end_date': str(end_d)
    }
    
    if selected_tab == "My History":
        filters['employee_id'] = current_emp_id
    elif role == 'Manager':
        # TODO: Filter by department
        pass
        
    history = attendance_model.get_history(filters)
    if history:
        df = pd.DataFrame(history)
        st.dataframe(df[['date', 'first_name', 'last_name', 'clock_in', 'clock_out', 'status', 'total_hours']], use_container_width=True)
    else:
        st.info("No records found for selected period.")
