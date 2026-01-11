from models.attendance import Attendance
from utils.calculators import calculate_work_hours
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    def __init__(self):
        self.attendance_model = Attendance()

    def clock_in(self, employee_id, location=None):
        """
        Record clock-in for an employee.
        """
        today = datetime.now().date()
        now = datetime.now()
        
        # Check if already clocked in
        existing = self.attendance_model.get_todays_record(employee_id, str(today))
        if existing:
            return False, "Already clocked in."
            
        # Shift Logic
        from models.employee import Employee
        from models.shift import Shift
        
        emp = Employee().get_by_id(employee_id)
        shift_id = emp.get('shift_id', 1)
        shift = Shift().get_by_id(shift_id)
        
        status = "Present"
        
        if shift:
            # Parse shift start time
            s_hour, s_min = map(int, shift['start_time'].split(':'))
            start_time = now.replace(hour=s_hour, minute=s_min, second=0, microsecond=0)
            grace = shift['grace_period_minutes']
            
            if now > start_time + timedelta(minutes=grace):
                status = "Late"
        else:
            # Fallback (9 AM)
            start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now > start_time + timedelta(minutes=15):
                status = "Late"
            
        data = {
            'employee_id': employee_id,
            'date': str(today),
            'clock_in': now, # timestamp
            'status': status,
            'work_type': 'Regular',
            'latitude': location[0] if location else None,
            'longitude': location[1] if location else None
        }
        
        try:
            self.attendance_model.create_record(data)
            return True, f"Clocked in successfully at {now.strftime('%H:%M')}"
        except Exception as e:
            logger.error(f"Clock in error: {e}")
            return False, f"System error: {str(e)}"

    def clock_out(self, employee_id):
        """
        Record clock-out and calculate hours.
        """
        today_date = datetime.now().date()
        date_str = str(today_date)
        
        record = self.attendance_model.get_todays_record(employee_id, date_str)
        if not record:
            return False, "No clock-in record found for today"
            
        if record['clock_out']:
             return False, "Already clocked out today"

        clock_out_time = datetime.now()
        
        # Parse clock_in from string if needed (SQLite returns strings for datetime)
        clock_in_time = record['clock_in']
        if isinstance(clock_in_time, str):
            try:
                clock_in_time = datetime.fromisoformat(clock_in_time)
            except ValueError:
                # Handle simplified format "YYYY-MM-DD HH:MM:SS.ssssss" or similar
                # Just a safeguard, creating a parser helper would be better
                pass

        # Calculate hours
        total, regular, overtime = calculate_work_hours(clock_in_time, clock_out_time)
        
        data = {
            'clock_out': clock_out_time,
            'total_hours': total,
            'regular_hours': regular,
            'overtime_hours': overtime
        }
        
        try:
            self.attendance_model.update_record(record['id'], data)
            return True, f"Clocked out at {clock_out_time.strftime('%H:%M')}. Worked {total} hours."
        except Exception as e:
            logger.error(f"Clock out error: {e}")
            return False, str(e)

    def get_employee_today(self, employee_id):
        """Get today's status for employee"""
        today = str(datetime.now().date())
        return self.attendance_model.get_todays_record(employee_id, today)
