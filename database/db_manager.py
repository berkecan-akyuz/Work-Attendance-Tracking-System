import sqlite3
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    def get_connection(self):
        """Create a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            return None

    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        """Execute a query with optional parameters"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            
            if fetch_all:
                result = cursor.fetchall()
                return [dict(row) for row in result] if result else []
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            logger.error(f"Database error executing query: {query}, Error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def execute_script(self, script_path):
        """Execute a SQL script from a file"""
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            with open(script_path, 'r') as f:
                script = f.read()
            
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
            logger.info(f"Successfully executed script: {script_path}")
            return True
        except Exception as e:
            logger.error(f"Error executing script {script_path}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
