from database.db_manager import DBManager

class Expense:
    def __init__(self):
        self.db = DBManager()

    def create(self, employee_id, date, amount, category, description, receipt_path=None):
        query = """
        INSERT INTO expenses (employee_id, date, amount, category, description, receipt_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (employee_id, date, amount, category, description, receipt_path))

    def get_by_employee(self, employee_id):
        return self.db.execute_query("SELECT * FROM expenses WHERE employee_id = ? ORDER BY date DESC", (employee_id,), fetch_all=True)

    def get_pending(self):
        query = """
        SELECT e.*, emp.first_name, emp.last_name 
        FROM expenses e
        JOIN employees emp ON e.employee_id = emp.id
        WHERE e.status = 'Pending'
        ORDER BY e.date ASC
        """
        return self.db.execute_query(query, fetch_all=True)
    
    def get_approved_for_month(self, month, year):
        # Format date filter is tricky with text dates 'YYYY-MM-DD'. 
        # Easier to fetch relevant and filter or use LIKE
        start = f"{year}-{month:02d}-01"
        # Simple string compare for month
        query = """
        SELECT * FROM expenses 
        WHERE status = 'Approved' AND strftime('%Y-%m', date) = ?
        """
        return self.db.execute_query(query, (f"{year}-{month:02d}",), fetch_all=True)

    def update_status(self, expense_id, status, approver_id=None):
        return self.db.execute_query(
            "UPDATE expenses SET status = ?, approved_by = ? WHERE id = ?", 
            (status, approver_id, expense_id)
        )
