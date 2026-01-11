from database.db_manager import DBManager

class SettingsModel:
    def __init__(self):
        self.db = DBManager()

    # --- System Settings --
    def get_system_settings(self):
        return self.db.execute_query("SELECT * FROM system_settings", fetch_all=True)

    def update_setting(self, key, value):
        return self.db.execute_query("UPDATE system_settings SET value = ? WHERE key = ?", (value, key))

    # --- Departments ---
    def get_departments(self):
        return self.db.execute_query("SELECT * FROM departments", fetch_all=True)

    def create_department(self, name, description):
        return self.db.execute_query("INSERT INTO departments (name, description) VALUES (?, ?)", (name, description))

    def delete_department(self, dept_id):
        return self.db.execute_query("DELETE FROM departments WHERE id = ?", (dept_id,))

    # --- Leave Types ---
    def get_leave_types(self):
        return self.db.execute_query("SELECT * FROM leave_types", fetch_all=True)

    def create_leave_type(self, name, days, is_paid):
        return self.db.execute_query(
            "INSERT INTO leave_types (name, days_allowed, is_paid) VALUES (?, ?, ?)", 
            (name, days, is_paid)
        )
    
    def delete_leave_type(self, type_id):
        return self.db.execute_query("DELETE FROM leave_types WHERE id = ?", (type_id,))
