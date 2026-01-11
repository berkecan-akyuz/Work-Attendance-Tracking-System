from database.db_manager import DBManager
import logging

logger = logging.getLogger(__name__)

class LeaveRequest:
    def __init__(self):
        self.db = DBManager()

    def create_request(self, data):
        """Create a new leave request"""
        query = """
        INSERT INTO leave_requests (
            employee_id, leave_type_id, start_date, end_date, total_days, reason, attachment_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            data['employee_id'],
            data['leave_type_id'],
            data['start_date'],
            data['end_date'],
            data['total_days'],
            data['reason'],
            data.get('attachment_path')
        ))

    def update_status(self, request_id, status, manager_comment=None):
        """Update request status (Approve/Reject)"""
        query = """
        UPDATE leave_requests 
        SET status = ?, manager_comment = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        return self.db.execute_query(query, (status, manager_comment, request_id))

    def get_requests(self, filters=None):
        """Get leave requests with filters"""
        query = """
        SELECT lr.*, e.first_name, e.last_name, lt.name as leave_type_name
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        JOIN leave_types lt ON lr.leave_type_id = lt.id
        WHERE 1=1
        """
        params = []
        if filters:
            if filters.get('employee_id'):
                query += " AND lr.employee_id = ?"
                params.append(filters['employee_id'])
            if filters.get('status'):
                query += " AND lr.status = ?"
                params.append(filters['status'])
            # Add date range logic if needed
        
        query += " ORDER BY lr.created_at DESC"
        return self.db.execute_query(query, tuple(params), fetch_all=True)

    def get_balance(self, employee_id, year):
        """
        Calculate leave balance. 
        Note: This is a simplified version. A real system needs a comprehensive accrual log.
        """
        # Get allowed days for each type
        types = self.get_all_leave_types()
        balances = []
        
        for lt in types:
            # Count days taken (Approved)
            query = """
            SELECT SUM(total_days) as used
            FROM leave_requests
            WHERE employee_id = ? AND leave_type_id = ? AND status = 'Approved'
            AND strftime('%Y', start_date) = ?
            """
            result = self.db.execute_query(query, (employee_id, lt['id'], str(year)), fetch_one=True)
            used = result['used'] if result and result['used'] else 0
            
            balances.append({
                'type_id': lt['id'],
                'type_name': lt['name'],
                'allowed': lt['days_allowed'],
                'used': used,
                'remaining': lt['days_allowed'] - used
            })
        return balances

    def get_all_leave_types(self):
        """Get all defined leave types"""
        query = "SELECT * FROM leave_types"
        return self.db.execute_query(query, fetch_all=True)
