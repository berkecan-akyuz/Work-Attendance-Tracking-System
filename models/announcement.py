from database.db_manager import DBManager
import streamlit as st

class Announcement:
    def __init__(self):
        self.db = DBManager()

    def create(self, title, message):
        user_id = st.session_state.user['id'] if 'user' in st.session_state and st.session_state.user else None
        query = "INSERT INTO announcements (title, message, created_by) VALUES (?, ?, ?)"
        return self.db.execute_query(query, (title, message, user_id))

    def get_active(self, limit=5):
        query = """
        SELECT * FROM announcements 
        WHERE is_active = 1 
        ORDER BY created_at DESC 
        LIMIT ?
        """
        return self.db.execute_query(query, (limit,), fetch_all=True)

    def get_all(self):
        return self.db.execute_query("SELECT * FROM announcements ORDER BY created_at DESC", fetch_all=True)

    def delete(self, announcement_id):
        # Soft delete or hard delete? Let's hard delete for simplicity or toggle active
        return self.db.execute_query("DELETE FROM announcements WHERE id = ?", (announcement_id,))
