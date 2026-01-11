from database.db_manager import DBManager
import streamlit as st
import json

class AuditLog:
    def __init__(self):
        self.db = DBManager()

    def log(self, action, target_table, target_id, details=None, user_id=None):
        """
        Log an action.
        user_id: Defaults to current logged in user if not provided.
        """
        if user_id is None:
            if 'user' in st.session_state and st.session_state.user:
                user_id = st.session_state.user['id']
            else:
                user_id = 0 # System or Unknown
                
        if isinstance(details, dict):
            details = json.dumps(details)
            
        return self.db.execute_query(
            "INSERT INTO audit_logs (user_id, action, target_table, target_id, details) VALUES (?, ?, ?, ?, ?)",
            (user_id, action, target_table, str(target_id), details)
        )

    def get_logs(self, limit=100):
        # Join with users to get names if possible
        query = """
        SELECT a.*, u.username, u.first_name, u.last_name 
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
        LIMIT ?
        """
        return self.db.execute_query(query, (limit,), fetch_all=True)
