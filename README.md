# 🏢 Work Attendance Tracking System (Enterprise Edition)

A robust, enterprise-grade Employee Management and Attendance Tracking system built with Python and Streamlit.

## 🚀 Key Features

### Core Modules
*   **⏰ Attendance Tracking**: Geolocation-tagged Clock In/Clock Out, Manual Entries, and Kiosk Mode with PIN.
*   **👥 Employee Management**: Full profile management, Shift assignment, and Role-based access (Admin/Manager/Employee).
*   **🏖️ Leave Management**: Request/Approve leave flows with balance tracking.
*   **💰 Payroll & Expenses**: 
    *   Automated monthly payroll calculation including Overtime.
    *   **Expense Reimbursements**: Employees capture receipts, Managers approve.
    *   **PDF Payslips**: Auto-generated payslips for download.
    *   **Dept Budgets**: Track actual spend vs allocated budget.

### Advanced Features
*   **🛡️ Document Vault**: Securely store Contracts, Tax forms, and ID copies.
*   **📅 Shift Calendar**: Visual team schedule.
*   **📢 Announcements**: Broadcasting system for effective communication.
*   **📊 Analytics Dashboard**: Real-time insights into attendance trends and department distribution.
*   **🔒 Security**: Role-Based Access Control (RBAC), Audit Logs, and Secure Password Hashing.

## 🛠️ Stack
*   **Frontend**: Streamlit
*   **Language**: Python 3.9+
*   **Database**: SQLite (Production-ready schema)
*   **Charting**: Plotly Express & Graph Objects
*   **PDF**: FPDF2

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/work-attendance-system.git
    cd work-attendance-system
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Database**
    The system auto-initializes `attendance.db` on first run. To verify schema:
    ```bash
    python initialize_db.py
    ```

5.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## 🔐 Credentials
**Default Admin Account** (Created on first initialization):
*   **Username**: `admin`
*   **Password**: `admin123`

## 📂 Project Structure
*   `app.py`: Main entry point (Login).
*   `pages/`: Application modules (Dashboard, Attendance, Payroll, etc.).
*   `models/`: Database interaction layers.
*   `services/`: Business logic (Payroll calculation, PDF generation).
*   `database/`: Schema and DB connection manager.
*   `utils/`: Helper functions (Auth, Validation).

## 🤝 Contribution
Feel free to fork and submit Pull Requests!

---
© 2026 Work Attendance System. Built for efficiency.
