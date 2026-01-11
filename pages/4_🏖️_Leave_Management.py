import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth_utils import require_login
from services.leave_service import LeaveService
from models.leave import LeaveRequest

# Page Config
st.set_page_config(page_title="Leave Management", page_icon="🏖️", layout="wide")
require_login()

from utils.auth_utils import render_sidebar
render_sidebar()

leave_service = LeaveService()
leave_model = LeaveRequest()
user = st.session_state.user
role = st.session_state.role
employee_id = user['employee_id']

st.title("🏖️ Leave Management")

if not employee_id and role != 'Admin':
    st.error("No employee record linked. Cannot manage leaves.")
    st.stop()

# --- Tabs ---
tabs = ["My Leaves", "New Request"]
if role in ['Admin', 'Manager']:
    tabs.append("Approval Queue")
    
selected_tab = st.radio("Navigation", tabs, horizontal=True)

if selected_tab == "My Leaves":
    st.subheader("My Leave Balance")
    
    # Fetch balance (Mocked or real if implemented)
    balances = leave_service.get_employee_balance(employee_id) if employee_id else []
    
    if balances:
        cols = st.columns(len(balances))
        for idx, bal in enumerate(balances):
            with cols[idx]:
                st.metric(bal['type_name'], f"{bal['remaining']} Days", f"Used: {bal['used']}")
    else:
        st.info("No leave balance information available.")
        
    st.subheader("My Request History")
    requests = leave_model.get_requests({'employee_id': employee_id}) if employee_id else []
    
    if requests:
        df = pd.DataFrame(requests)
        st.dataframe(df[['leave_type_name', 'start_date', 'end_date', 'total_days', 'status', 'reason']], use_container_width=True)
    else:
        st.info("No leave requests found.")

elif selected_tab == "New Request":
    st.subheader("Submit Leave Request")
    
    with st.form("leave_request_form"):
        # Fetch leave types
        leave_types = leave_model.get_all_leave_types()
        type_options = {lt['id']: lt['name'] for lt in leave_types}
        
        c1, c2 = st.columns(2)
        with c1:
            lt_id = st.selectbox("Leave Type", options=list(type_options.keys()), format_func=lambda x: type_options[x])
        
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("Start Date", min_value=datetime.now())
        with c2:
            end_date = st.date_input("End Date", min_value=datetime.now())
            
        reason = st.text_area("Reason")
        uploaded_file = st.file_uploader("Attach Document (Medical Cert, etc.)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if not reason:
                st.error("Please provide a reason.")
            else:
                attachment_path = None
                if uploaded_file:
                    import os
                    import uuid
                    ext = uploaded_file.name.split('.')[-1]
                    filename = f"{uuid.uuid4()}.{ext}"
                    save_path = os.path.join("assets", "uploads", filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    attachment_path = save_path
                
                success, msg = leave_service.submit_request(employee_id, lt_id, start_date, end_date, reason, attachment_path)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

elif selected_tab == "Approval Queue":
    st.subheader("Pending Approvals")
    
    # Fetch pending requests
    pending = leave_model.get_requests({'status': 'Pending'})
    
    if pending:
        for req in pending:
            with st.expander(f"{req['first_name']} {req['last_name']} - {req['leave_type_name']} ({req['total_days']} days)"):
                c1, c2 = st.columns(2)
                c1.write(f"**Dates:** {req['start_date']} to {req['end_date']}")
                c1.write(f"**Reason:** {req['reason']}")
                
                if 'attachment_path' in req and req['attachment_path']:
                    import os
                    if os.path.exists(req['attachment_path']):
                        with open(req['attachment_path'], "rb") as f:
                            btn = st.download_button(
                                label="📎 Download Attachment",
                                data=f,
                                file_name=os.path.basename(req['attachment_path']),
                                mime="application/octet-stream"
                            )
                
                start = datetime.strptime(req['start_date'], '%Y-%m-%d')
                end = datetime.strptime(req['end_date'], '%Y-%m-%d')
                days_label = f"{(end-start).days + 1} Days"
                c2.caption(days_label)
                
                col_a, col_b, col_c = st.columns([1, 1, 3])
                if col_a.button("✅ Approve", key=f"app_{req['id']}"):
                    leave_service.process_request(req['id'], 'Approved')
                    st.success("Approved")
                    st.rerun()
                    
                if col_b.button("❌ Reject", key=f"rej_{req['id']}"):
                    leave_service.process_request(req['id'], 'Rejected')
                    st.warning("Rejected")
                    st.rerun()
    else:
        st.info("No pending requests.")
