import streamlit as st
from services.auth_service import AuthService
from config import PAGE_TITLE, PAGE_ICON, LAYOUT
import time

# Page Configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="collapsed"
)

# Initialize Services
auth_service = AuthService()

def init_session():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    # Hide sidebar if not authenticated
    if not st.session_state.authenticated:
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {display: none;}
                [data-testid="collapsedControl"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True
        )

def login_page():
    """Render the login page"""
    st.markdown("""
        <style>
        a.anchor-link { display: none !important; visibility: hidden !important; }
        [data-testid="stMarkdownContainer"] a[href^="#"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)
        
    st.title("🔐 Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### Welcome Back!")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        user = auth_service.login(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.role = user['role']
                            st.success(f"Welcome, {user['username']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
        
        st.markdown("---")
        if st.button("📱 Switch to Kiosk Mode", use_container_width=True):
            st.switch_page("pages/9_📱_Kiosk.py")

def main():
    init_session()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # Safety check for invalid session state
        if st.session_state.user is None:
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()
            return

        # Logged in View
        display_name = st.session_state.user['first_name'] if st.session_state.user['first_name'] else st.session_state.user['username']
        
        # Determine effective role for testing/seeding context if needed or just display
        
        # Render Sidebar
        from utils.auth_utils import render_sidebar
        render_sidebar()
        
        st.title(f"👋 Welcome, {display_name}!")
        
        st.markdown("""
        ### Work Attendance Tracking System
        
        Use the sidebar to navigate to different sections:
        
        - **🏠 Dashboard**: View your statistics and overview
        - **⏰ Attendance**: specific clock-in/out and history
        - **🏖️ Leave Management**: Request and manage leaves
        - **📊 Reports**: Generate attendance reports
        
        """)
        
        # Sidebar Info
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**User:** {st.session_state.user['username']}")
        st.sidebar.markdown(f"**Role:** {st.session_state.role}")

if __name__ == "__main__":
    main()
