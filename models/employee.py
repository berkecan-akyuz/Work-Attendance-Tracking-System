from database.db_manager import DBManager
import logging

logger = logging.getLogger(__name__)

class Employee:
    def __init__(self):
        self.db = DBManager()

    def create_employee(self, data):
        """Create a new employee"""
        query = """
        INSERT INTO employees (
            first_name, last_name, email, phone, national_id, address,
            employee_code, department_id, position, hire_date, salary, hourly_rate, 
            status, shift_id, pin_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data['first_name'], data['last_name'], data['email'], data['phone'],
            data['national_id'], data['address'], data['employee_code'],
            data['department_id'], data['position'], data['hire_date'],
            data['salary'], data['hourly_rate'], data['status'],
            data.get('shift_id', 1), data.get('pin_code')
        )
        return self.db.execute_query(query, params)

    def get_all(self, active_only=False):
        """Get all employees"""
        query = """
        SELECT e.*, d.name as department_name 
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        """
        if active_only:
            query += " WHERE e.status = 'Active'"
        query += " ORDER BY e.last_name, e.first_name"
        return self.db.execute_query(query, fetch_all=True)

    def get_by_id(self, employee_id):
        """Get employee by ID"""
        query = """
        SELECT e.*, d.name as department_name 
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.id = ?
        """
        return self.db.execute_query(query, (employee_id,), fetch_one=True)
    
    def get_by_email(self, email):
        """Get employee by email"""
        query = "SELECT * FROM employees WHERE email = ?"
        return self.db.execute_query(query, (email,), fetch_one=True)

    def update_employee(self, employee_id, data):
        """Update employee details"""
        fields = []
        params = []
        for key, value in data.items():
            fields.append(f"{key} = ?")
            params.append(value)
        
        params.append(employee_id)
        query = f"UPDATE employees SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        res = self.db.execute_query(query, tuple(params))
        
        # Audit Log
        try:
            from models.audit import AuditLog
            audit = AuditLog()
            audit.log("UPDATE", "employees", employee_id, details=f"Updated fields: {list(data.keys())}")
        except Exception as e:
            pass
            
        return res

    def delete_employee(self, employee_id):
        """Soft delete employee (set to Inactive)"""
        query = "UPDATE employees SET status = 'Inactive', updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.db.execute_query(query, (employee_id,))
