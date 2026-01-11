import streamlit as st

def require_login():
    """
    Check if user is authenticated. 
    If not, show warning and stop execution.
    Should be called at the start of every page.
    """
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please login to access this page.")
        if st.button("Go to Login Page"):
            st.switch_page("app.py")
        st.stop()

def check_role(allowed_roles):
    """
    Check if current user has one of the allowed roles.
    allowed_roles: list of strings (e.g. ['Admin', 'Manager'])
    """
    if st.session_state.role not in allowed_roles:
        st.error("You do not have permission to access this page.")
        st.stop()

def render_sidebar():
    """Render the sidebar navigation based on role"""
    role = st.session_state.get('role')
    
    # st.sidebar.title("Navigation") # Optional header
    
    # Define pages and permissions
    # Format: Path, Label, Icon, Allowed Roles
    # If Allowed Roles is None, everyone can access (if logged in logic handled)
    pages = [
        #("app.py", "Home", "🏠", None), # Hidden to avoid confusion. Dashboard is home.
        ("pages/1_🏠_Dashboard.py", "Dashboard", "📊", None),
        ("pages/2_👥_Employees.py", "Employees", "👥", ['Admin', 'Manager']),
        ("pages/3_⏰_Attendance.py", "Attendance", "⏰", None),
        ("pages/4_🏖️_Leave_Management.py", "Leave Management", "🏖️", None),
        ("pages/5_📊_Reports.py", "Reports", "📈", ['Admin', 'Manager']),
        ("pages/6_⚙️_Settings.py", "Settings", "⚙️", ['Admin']),
        ("pages/8_💰_Payroll.py", "Payroll", "💰", ['Admin', 'Manager']),
        ("pages/7_👤_Profile.py", "Profile", "👤", None),
        ("pages/10_📢_Announcements.py", "Announcements", "📢", ['Admin']),
        ("pages/11_🛡️_Audit_Logs.py", "Audit Logs", "🛡️", ['Admin']),
        ("pages/12_👤_User_Management.py", "User Management", "👤", ['Admin']),
        ("pages/13_💸_Expenses.py", "Expenses", "💸", None),
    ]

    with st.sidebar:
        # Hide Anchor Links Global CSS - "Nuclear" Option
        st.markdown("""
            <style>
            /* Type 1: Standard Streamlit Anchors */
            a.anchor-link { display: none !important; visibility: hidden !important; width: 0 !important; }
            /* Type 2: Newer Streamlit versions */
            [data-testid="stMarkdownContainer"] a[href^="#"] { display: none !important; }
            /* Header adjustments */
            h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a { display: none !important; }
            
            [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
            </style>
            """, unsafe_allow_html=True)
            
        # Branding (Logo)
        from database.db_manager import DBManager
        import os
        try:
            db = DBManager()
            logo_setting = db.execute_query("SELECT value FROM system_settings WHERE key = 'company_logo'", fetch_one=True)
            if logo_setting and os.path.exists(logo_setting['value']):
                st.image(logo_setting['value'], use_column_width=True)
        except Exception:
            pass # Fail silently for logo

        st.markdown("### Navigation")
        
        for path, label, icon, roles in pages:
            if roles is None or (role and role in roles):
                st.page_link(path, label=label, icon=icon)

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.role = None
            st.switch_page("app.py")
