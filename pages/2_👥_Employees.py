import streamlit as st
import pandas as pd
from utils.auth_utils import require_login, check_role
from models.employee import Employee
from models.attendance import Attendance
from models.shift import Shift
from utils.validators import validate_email, validate_phone

# Page Config
st.set_page_config(page_title="Employees", page_icon="👥", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

check_role(['Admin', 'Manager']) # Only admins and managers can access

employee_model = Employee()

# Session State for Form Handling
if 'show_employee_form' not in st.session_state:
    st.session_state.show_employee_form = False
if 'editing_employee' not in st.session_state:
    st.session_state.editing_employee = None

def toggle_form(employee=None):
    st.session_state.show_employee_form = not st.session_state.show_employee_form
    st.session_state.editing_employee = employee

def render_employee_form():
    is_edit = st.session_state.editing_employee is not None
    emp = st.session_state.editing_employee if is_edit else {}
    
    st.subheader("Edit Employee" if is_edit else "Add New Employee")
    
    with st.form("employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", value=emp.get('first_name', ''))
            last_name = st.text_input("Last Name*", value=emp.get('last_name', ''))
            email = st.text_input("Email*", value=emp.get('email', ''))
            phone = st.text_input("Phone", value=emp.get('phone', ''))
            national_id = st.text_input("National ID", value=emp.get('national_id', ''))
            address = st.text_area("Address", value=emp.get('address', ''))
            
        with col2:
            employee_code = st.text_input("Employee Code*", value=emp.get('employee_code', ''))
            # Fetch departments properly in real app, placeholder for now
            department_id = st.number_input("Department ID", value=emp.get('department_id', 1), min_value=1)
            position = st.text_input("Position", value=emp.get('position', ''))
            hire_date = st.date_input("Hire Date", value=pd.to_datetime(emp.get('hire_date')) if emp.get('hire_date') else None)
            salary = st.number_input("Monthly Salary", value=float(emp.get('salary', 0.0)))
            hourly_rate = st.number_input("Hourly Rate", value=float(emp.get('hourly_rate', 0.0)))
            status_options = ["Active", "Inactive", "Terminated"] # Updated status options
            status = st.selectbox("Status", status_options, index=status_options.index(emp.get('status', 'Active')))

            # New Fields: Shift and PIN
            shifts_data = Shift().get_all()
            shift_options = {s['id']: f"{s['name']} ({s['start_time']}-{s['end_time']})" for s in shifts_data} if shifts_data else {1: "Default Shift (8:00-17:00)"}
            
            # Determine initial shift selection
            current_shift_id = emp.get('shift_id', 1)
            if current_shift_id not in shift_options:
                # If the employee's current shift_id is not in available options, default to the first available or 1
                current_shift_id = list(shift_options.keys())[0] if shift_options else 1
            
            shift_id = st.selectbox("Shift", options=list(shift_options.keys()), format_func=lambda x: shift_options[x], index=list(shift_options.keys()).index(current_shift_id))
            pin = st.text_input("Kiosk PIN Code", value=emp.get('pin_code', ''))

        submitted = st.form_submit_button("Save Employee")
        
        if submitted:
            # Validation
            if not first_name or not last_name or not email or not employee_code:
                st.error("Please fill in all required fields (*)")
            elif not validate_email(email):
                st.error("Invalid email format")
            else:
                data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'national_id': national_id,
                    'address': address,
                    'employee_code': employee_code,
                    'department_id': department_id,
                    'position': position,
                    'hire_date': str(hire_date),
                    'salary': salary,
                    'hourly_rate': hourly_rate,
                    'status': status
                }
                
                try:
                    if is_edit:
                        employee_model.update_employee(emp['id'], data)
                        st.success("Employee updated successfully!")
                    else:
                        employee_model.create_employee(data)
                        st.success("Employee created successfully!")
                    
                    st.session_state.show_employee_form = False
                    st.session_state.editing_employee = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving employee: {e}")
        
    if st.button("Cancel"):
        st.session_state.show_employee_form = False
        st.session_state.editing_employee = None
        st.rerun()

def render_employee_list():
    st.title("👥 Employee Management")
    
    col_act, col_search = st.columns([1, 3])
    with col_act:
        if st.button("➕ Add New Employee"):
            toggle_form()
            st.rerun()
            
    with col_search:
        search_term = st.text_input("Search (Name, Email, Code)", placeholder="Type to search...")

    employees = employee_model.get_all()
    
    # Filtering (Client-side for MVP)
    if search_term:
        term = search_term.lower()
        employees = [e for e in employees if 
                     term in e['first_name'].lower() or 
                     term in e['last_name'].lower() or 
                     term in e['email'].lower() or
                     term in e['employee_code'].lower()]

    if employees:
        df = pd.DataFrame(employees)
        # Display selected columns
        display_cols = ['employee_code', 'first_name', 'last_name', 'email', 'department_name', 'position', 'status']
        # Map DB columns to Display columns if needed, but for now just showing raw
        
        st.dataframe(df[display_cols], use_container_width=True)
        
        # Actions for selected employee
        st.markdown("### Actions")
        
        selected_id = st.selectbox("Select Employee to specific action action", options=[e['id'] for e in employees], format_func=lambda x: next((f"{e['first_name']} {e['last_name']}" for e in employees if e['id'] == x), str(x)))
        
        c1, c2, c3 = st.columns(3)
        if c1.button("✏️ Edit Selected"):
            selected_emp = next((e for e in employees if e['id'] == selected_id), None)
            if selected_emp:
                toggle_form(dict(selected_emp)) # convert Row to dict
                st.rerun()
                
        if c2.button("🗑️ Delete (Deactivate)"):
            if st.warning("Are you sure you want to deactivate this employee?"):
                employee_model.delete_employee(selected_id)
                st.success("Employee deactivated.")
                st.rerun()

    else:
        st.info("No employees found.")

if st.session_state.show_employee_form:
    render_employee_form()
else:
    render_employee_list()
