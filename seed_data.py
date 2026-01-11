from database.db_manager import DBManager
from services.auth_service import AuthService
from models.employee import Employee
import random
from datetime import datetime

db = DBManager()
auth = AuthService()
emp_model = Employee()

def seed():
    print("🌱 Seeding Database with Demo Data...")

    # 1. Departments
    depts = [
        ('Engineering', 50000), 
        ('HR', 10000), 
        ('Sales', 30000), 
        ('Marketing', 20000)
    ]
    dept_ids = {}
    for name, budget in depts:
        try:
            db.execute_query("INSERT OR IGNORE INTO departments (name, budget) VALUES (?, ?)", (name, budget))
            res = db.execute_query("SELECT id FROM departments WHERE name = ?", (name,), fetch_one=True)
            dept_ids[name] = res['id']
        except Exception:
            pass

    # 2. Users & Employees from credentials.txt
    # (Based on the list I saw in step 799)
    users = [
        # (First, Last, Role, Dept)
        ("Admin", "User", "Admin", "HR"),
        ("Manager", "User", "Manager", "HR"),
        ("Mary", "Garcia", "Employee", "Sales"),
        ("Richard", "Thomas", "Employee", "Engineering"),
        ("Jessica", "Jackson", "Employee", "Marketing"),
        ("Joseph", "Moore", "Employee", "Sales"),
        ("James", "Williams", "Employee", "Engineering"),
    ]
    
    # Common password
    password = "password123"

    for first, last, role, dept in users:
        username = f"{first.lower()}.{last.lower()}"
        if role == 'Admin': username = 'admin'; password='admin123'
        
        # Check if user exists
        existing = db.execute_query("SELECT id FROM users WHERE username = ?", (username,), fetch_one=True)
        
        if not existing:
            print(f"Creating user: {username} ({role})")
            # Create User
            user_id = auth.register_user(username, password, role)
            
            # Create Employee Profile (for non-admins, or link admin too)
            # Generate fake data
            code = f"EMP{random.randint(1000,9999)}"
            emp_data = {
                'first_name': first,
                'last_name': last,
                'email': f"{username}@company.com",
                'phone': f"555-01{random.randint(10,99)}",
                'national_id': f"ID{random.randint(10000,99999)}",
                'address': "123 Demo St",
                'employee_code': code,
                'department_id': dept_ids.get(dept, 1),
                'position': role,
                'hire_date': str(datetime.now().date()),
                'salary': random.randint(3000, 8000),
                'hourly_rate': random.randint(20, 50),
                'status': 'Active',
                'pin_code': str(random.randint(1000, 9999))
            }
            
            # Direct insert via model to handle linking
            try:
                emp_model.create_employee(emp_data)
                # Link
                new_emp = db.execute_query("SELECT id FROM employees WHERE employee_code = ?", (code,), fetch_one=True)
                if new_emp:
                    db.execute_query("UPDATE users SET employee_id = ? WHERE id = ?", (new_emp['id'], user_id))
            except Exception as e:
                print(f"Failed to create employee for {username}: {e}")
        else:
            print(f"User {username} already exists.")

    print("✅ Seeding Complete.")

if __name__ == "__main__":
    seed()
