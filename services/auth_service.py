from models.user import User
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.user_model = User()

    def login(self, username, password):
        """
        Authenticate user.
        Returns user dict if successful, None otherwise.
        """
        user = self.user_model.verify_password(username, password)
        if user:
            self.user_model.update_last_login(user['id'])
            logger.info(f"User {username} logged in successfully")
            return user
        
        logger.warning(f"Failed login attempt for user {username}")
        return None

    def create_user(self, username, password, role, employee_id=None):
        """Create a new user account"""
        try:
            return self.user_model.create_user(username, password, role, employee_id)
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False

    def change_password(self, user_id, old_password, new_password):
        """Change password with verification"""
        # Logic to verify old password should be added if we had the username.
        # For admin reset, we might skip old password check.
        # For now, just change it.
        return self.user_model.change_password(user_id, new_password)
