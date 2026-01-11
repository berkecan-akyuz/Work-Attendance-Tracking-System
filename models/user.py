from database.db_manager import DBManager
import bcrypt
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self):
        self.db = DBManager()

    def create_user(self, username, password, role, employee_id=None):
        """Create a new user"""
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = """
        INSERT INTO users (username, password_hash, role, employee_id)
        VALUES (?, ?, ?, ?)
        """
        return self.db.execute_query(query, (username, hashed, role, employee_id))

    def get_by_username(self, username):
        """Get user by username"""
        query = """
        SELECT u.*, e.first_name, e.last_name 
        FROM users u 
        LEFT JOIN employees e ON u.employee_id = e.id
        WHERE u.username = ?
        """
        return self.db.execute_query(query, (username,), fetch_one=True)
    
    def get_by_id(self, user_id):
        """Get user by ID"""
        query = """
        SELECT u.*, e.first_name, e.last_name 
        FROM users u 
        LEFT JOIN employees e ON u.employee_id = e.id
        WHERE u.id = ?
        """
        return self.db.execute_query(query, (user_id,), fetch_one=True)

    def verify_password(self, username, password):
        """Verify password for a user"""
        user = self.get_by_username(username)
        if not user or not user['is_active']:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
        return None

    def update_last_login(self, user_id):
        """Update last login timestamp"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.db.execute_query(query, (user_id,))

    def change_password(self, user_id, new_password):
        """Change user password"""
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = "UPDATE users SET password_hash = ? WHERE id = ?"
        return self.db.execute_query(query, (hashed, user_id))
    
    def get_all_users(self):
        """Get all users"""
        query = """
        SELECT u.*, e.first_name, e.last_name 
        FROM users u 
        LEFT JOIN employees e ON u.employee_id = e.id
        ORDER BY u.username
        """
        return self.db.execute_query(query, fetch_all=True)
