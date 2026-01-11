from fpdf import FPDF
import os

class PDFService(FPDF):
    def header(self):
        # Company Name
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Work Attendance Corp', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def generate_payslip(self, employee, payroll_data, month_year):
        self.add_page()
        
        # Title
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, f'PAYSLIP - {month_year}', 0, 1, 'C')
        self.ln(5)
        
        # Employee Details Box
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, "Employee Details", 0, 1)
        self.set_font('Arial', '', 10)
        self.cell(40, 6, "Name:", 0)
        self.cell(0, 6, payroll_data['Name'], 0, 1)
        self.cell(40, 6, "Employee ID:", 0)
        self.cell(0, 6, payroll_data['Employee ID'], 0, 1)
        self.cell(40, 6, "Department:", 0)
        self.cell(0, 6, payroll_data['Department'], 0, 1)
        self.ln(10)
        
        # Earnings Table Header
        self.set_fill_color(200, 220, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(100, 8, "Description", 1, 0, 'L', True)
        self.cell(40, 8, "Hours", 1, 0, 'C', True)
        self.cell(50, 8, "Amount ($)", 1, 1, 'R', True)
        
        # Earnings Rows
        self.set_font('Arial', '', 10)
        
        # Regular
        reg_hrs = float(payroll_data.get('Regular Hours', 0))
        rate = float(payroll_data.get('Hourly Rate', 0))
        reg_pay = reg_hrs * rate
        self.cell(100, 8, "Regular Pay", 1)
        self.cell(40, 8, f"{reg_hrs:.2f}", 1, 0, 'C')
        self.cell(50, 8, f"{reg_pay:.2f}", 1, 1, 'R')
        
        # Overtime
        ot_hrs = float(payroll_data.get('Overtime Hours', 0))
        ot_pay = ot_hrs * rate * 1.5 # Assuming 1.5x
        if ot_hrs > 0:
            self.cell(100, 8, "Overtime Pay (1.5x)", 1)
            self.cell(40, 8, f"{ot_hrs:.2f}", 1, 0, 'C')
            self.cell(50, 8, f"{ot_pay:.2f}", 1, 1, 'R')
            
        # Gross
        gross = float(payroll_data.get('Gross Pay', 0))
        self.set_font('Arial', 'B', 10)
        self.cell(140, 8, "Gross Pay", 1, 0, 'R')
        self.cell(50, 8, f"{gross:.2f}", 1, 1, 'R')
        
        self.ln(5)
        
        # Deductions (Simplified)
        self.set_fill_color(255, 220, 220)
        self.cell(140, 8, "Tax Deduction (Est. 20%)", 1, 0, 'L', True)
        tax = float(payroll_data.get('Tax (Est. 20%)', 0))
        self.cell(50, 8, f"-{tax:.2f}", 1, 1, 'R', True)
        
        # Reimbursements
        reimb = float(payroll_data.get('Reimbursements', 0))
        if reimb > 0:
            self.set_fill_color(220, 255, 220)
            self.cell(140, 8, "Expense Reimbursements (Tax Free)", 1, 0, 'L', True)
            self.cell(50, 8, f"+{reimb:.2f}", 1, 1, 'R', True)
        
        self.ln(2)
        
        # Net Pay
        self.set_fill_color(220, 255, 220)
        self.set_font('Arial', 'B', 12)
        self.cell(140, 12, "NET PAY", 1, 0, 'R', True)
        net = float(payroll_data.get('Net Pay', 0))
        self.cell(50, 12, f"${net:.2f}", 1, 1, 'R', True)
        
        self.ln(20)
        
        # Signatures
        self.set_font('Arial', '', 10)
        self.cell(90, 8, "_________________________", 0, 0, 'C')
        self.cell(90, 8, "_________________________", 0, 1, 'C')
        self.cell(90, 5, "Employer Signature", 0, 0, 'C')
        self.cell(90, 5, "Employee Signature", 0, 1, 'C')
        
        # fpdf output(dest='S') might return bytearray or string depending on version.
        # If it returns a string (latin-1), we encode it.
        # If it returns a bytearray, we just convert to bytes.
        out = self.output(dest='S')
        if isinstance(out, str):
            return out.encode('latin-1')
        return bytes(out)
