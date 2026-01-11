from models.leave import LeaveRequest
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LeaveService:
    def __init__(self):
        self.leave_model = LeaveRequest()

    def submit_request(self, employee_id, leave_type_id, start_date, end_date, reason, attachment_path=None):
        """Submit a new leave request"""
        # Calculate days
        # This is a simplified calculation, a real one would skip weekends/holidays
        start = datetime.strptime(str(start_date), '%Y-%m-%d')
        end = datetime.strptime(str(end_date), '%Y-%m-%d')
        total_days = (end - start).days + 1
        
        if total_days <= 0:
            return False, "End date must be after start date"

        # Check balance
        # In a real app, we'd check if they have enough balance here
        
        data = {
            'employee_id': employee_id,
            'leave_type_id': leave_type_id,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'total_days': total_days,
            'reason': reason,
            'attachment_path': attachment_path
        }
        
        try:
            self.leave_model.create_request(data)
            return True, "Leave request submitted successfully"
        except Exception as e:
            logger.error(f"Submit leave error: {e}")
            return False, str(e)

    def process_request(self, request_id, action, manager_comment=""):
        """Approve or Reject a request"""
        if action not in ['Approved', 'Rejected']:
            return False, "Invalid action"
            
        try:
            self.leave_model.update_status(request_id, action, manager_comment)
            return True, f"Request {action} successfully"
        except Exception as e:
            logger.error(f"Process leave error: {e}")
            return False, str(e)

    def get_employee_balance(self, employee_id):
        """Get leave balance for employee"""
        year = datetime.now().year
        return self.leave_model.get_balance(employee_id, year)
