from database.db_manager import DBManager
import os
import bcrypt

def init():
    print("Initializing database...")
    db = DBManager()
    schema_path = os.path.join('database', 'schema.sql')
    
    if not os.path.exists(schema_path):
        print(f"Error: Schema file not found at {schema_path}")
        return

    # Run schema
    if not db.execute_script(schema_path):
        print("Failed to execute schema.")
        return

    # Check if admin exists
    admin = db.execute_query("SELECT * FROM users WHERE username = ?", ('admin',), fetch_one=True)
    if not admin:
        # Create default admin
        password = b"admin123"
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        
        query = """
        INSERT INTO users (username, password_hash, role) 
        VALUES (?, ?, ?)
        """
        db.execute_query(query, ('admin', hashed, 'Admin'))
        print("Default admin created (admin/admin123).")
    else:
        print("Admin user already exists.")

    print("Database initialization complete.")

if __name__ == "__main__":
    init()
