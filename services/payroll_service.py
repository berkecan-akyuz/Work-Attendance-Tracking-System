from models.employee import Employee
from models.attendance import Attendance
from utils.calculators import calculate_salary
from datetime import datetime, timedelta
import pandas as pd

class PayrollService:
    def __init__(self):
        self.emp_model = Employee()
        self.att_model = Attendance()

    def generate_payroll(self, year, month):
        """
        Generate payroll report for a specific month.
        Returns a list of dictionaries with payroll details.
        """
        # Define date range
        start_date = datetime(year, month, 1).date()
        # Get end date (first day of next month - 1 day)
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
        str_start = str(start_date)
        str_end = str(end_date)
        
        employees = self.emp_model.get_all(active_only=True)
        payroll_data = []
        
        
        # 1. Fetch ALL attendance for this period in one go
        # Note: We need a method to get ALL history for range, not filtered by one employee ID yet.
        # existing get_history supports filters. If we omit employee_id, it should return all.
        all_attendance = self.att_model.get_history({
            'start_date': str_start,
            'end_date': str_end
        })
        
        # 2. Fetch ALL approved expenses for this period
        from models.expense import Expense
        exp_model = Expense()
        all_expenses = exp_model.get_approved_for_month(month, year) # Already returns list
        
        payroll_data = []
        
        for emp in employees:
            # Filter in Python (fast for <10k records)
            emp_recs = [r for r in all_attendance if r['employee_id'] == emp['id']]
            emp_exps = [x['amount'] for x in all_expenses if x['employee_id'] == emp['id']]
            
            # Aggregate hours
            total_reg = sum(r['regular_hours'] for r in emp_recs if r['regular_hours'])
            total_ot = sum(r['overtime_hours'] for r in emp_recs if r['overtime_hours'])
            
            hourly_rate = emp['hourly_rate'] if emp['hourly_rate'] else 0.0
            
            # Calculate Pay
            gross_pay = calculate_salary(hourly_rate, total_reg, total_ot)
            
            total_reimbursement = sum(emp_exps)
            
            # Simple tax estimation (e.g. 20% flat for demo)
            tax = round(gross_pay * 0.20, 2)
            net_pay = round(gross_pay - tax + total_reimbursement, 2)
            
            payroll_data.append({
                'Employee ID': emp['employee_code'],
                'Name': f"{emp['first_name']} {emp['last_name']}",
                'Department': emp['department_name'],
                'Regular Hours': round(total_reg, 2),
                'Overtime Hours': round(total_ot, 2),
                'Hourly Rate': hourly_rate,
                'Gross Pay': gross_pay,
                'Tax (Est. 20%)': tax,
                'Reimbursements': round(total_reimbursement, 2),
                'Net Pay': net_pay
            })
            
        return payroll_data
