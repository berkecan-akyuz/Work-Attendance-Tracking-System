import streamlit as st
import pandas as pd
from utils.auth_utils import require_login, check_role, render_sidebar
from models.audit import AuditLog

st.set_page_config(page_title="Audit Logs", page_icon="🛡️", layout="wide")
require_login()
render_sidebar()
check_role(['Admin'])

st.title("🛡️ Security Audit Logs")

audit = AuditLog()
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
