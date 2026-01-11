from database.db_manager import DBManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Attendance:
    def __init__(self):
        self.db = DBManager()

    def create_record(self, data):
        """Create a new attendance record (e.g. clock in)"""
        query = """
        INSERT INTO attendance (
            employee_id, date, clock_in, clock_out, status, work_type, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            data['employee_id'], 
            data['date'], 
            data['clock_in'],
            data.get('clock_out'), # Added clock_out
            data['status'],
            data.get('work_type', 'Regular'),
            data.get('latitude'),
            data.get('longitude')
        ))

    def update_record(self, attendance_id, data):
        """Update attendance record (e.g. clock out, add break)"""
        fields = []
        params = []
        for key, value in data.items():
            fields.append(f"{key} = ?")
            params.append(value)
        
        params.append(attendance_id)
        query = f"UPDATE attendance SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.db.execute_query(query, tuple(params))

    def get_todays_record(self, employee_id, date_str):
        """Get attendance record for a specific employee and date"""
        query = "SELECT * FROM attendance WHERE employee_id = ? AND date = ?"
        return self.db.execute_query(query, (employee_id, date_str), fetch_one=True)

    def get_history(self, filters=None):
        """
        Get attendance history with optional filters.
        filters: dict containing 'start_date', 'end_date', 'employee_id', 'department_id'
        """
        query = """
        SELECT a.*, e.first_name, e.last_name, e.employee_code, d.name as department_name
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE 1=1
        """
        params = []
        
        if filters:
            if filters.get('start_date'):
                query += " AND a.date >= ?"
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += " AND a.date <= ?"
                params.append(filters['end_date'])
            if filters.get('employee_id'):
                query += " AND a.employee_id = ?"
                params.append(filters['employee_id'])
            if filters.get('department_id'):
                query += " AND e.department_id = ?"
                params.append(filters['department_id'])
        
        query += " ORDER BY a.date DESC, a.clock_in DESC"
        return self.db.execute_query(query, tuple(params), fetch_all=True)

    def get_pending_approvals(self, manager_id=None):
        """Get records needing approval"""
        query = """
        SELECT a.*, e.first_name, e.last_name 
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        WHERE a.is_approved = 0
        """
        # If manager_id provided, filter by department (logic to be enhanced)
        query += " ORDER BY a.date ASC"
        return self.db.execute_query(query, fetch_all=True)
