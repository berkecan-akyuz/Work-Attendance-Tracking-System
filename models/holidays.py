from database.db_manager import DBManager

class Holiday:
    def __init__(self):
        self.db = DBManager()

    def get_all(self, year=None):
        if year:
            return self.db.execute_query("SELECT * FROM public_holidays WHERE year = ? ORDER BY date", (year,), fetch_all=True)
        return self.db.execute_query("SELECT * FROM public_holidays ORDER BY date", fetch_all=True)

    def add(self, date, name, year):
        return self.db.execute_query(
            "INSERT INTO public_holidays (date, name, year) VALUES (?, ?, ?)",
            (date, name, year)
        )

    def delete(self, holiday_id):
        return self.db.execute_query("DELETE FROM public_holidays WHERE id = ?", (holiday_id,))

    def is_holiday(self, date_str):
        # date_str: YYYY-MM-DD
        res = self.db.execute_query("SELECT id FROM public_holidays WHERE date = ?", (date_str,), fetch_one=True)
        return res is not None
