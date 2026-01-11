from database.db_manager import DBManager

class Shift:
    def __init__(self):
        self.db = DBManager()

    def get_all(self):
        return self.db.execute_query("SELECT * FROM shifts", fetch_all=True)

    def get_by_id(self, shift_id):
        return self.db.execute_query("SELECT * FROM shifts WHERE id = ?", (shift_id,), fetch_one=True)

    def create(self, name, start_time, end_time, grace_period):
        return self.db.execute_query(
            "INSERT INTO shifts (name, start_time, end_time, grace_period_minutes) VALUES (?, ?, ?, ?)",
            (name, start_time, end_time, grace_period)
        )

    def delete(self, shift_id):
        # Could check if used by employees first
        return self.db.execute_query("DELETE FROM shifts WHERE id = ?", (shift_id,))
