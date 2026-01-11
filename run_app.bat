@echo off
setlocal

echo ===================================================
echo 🚀 Work Attendance System - One-Click Launcher
echo ===================================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from python.org
    pause
    exit /b
)

REM Create Virtual Environment if not exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
    echo [OK] Virtual environment created.
)

REM Activate Venv and Install Requirements
echo [INFO] Checking dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b
)
echo [OK] Dependencies installed.

REM Run Database Migrations (Sequentially to ensure latest schema)
echo [INFO] Verification Database Schema...
python initialize_db.py >nul 2>&1
python seed_data.py >nul 2>&1
REM (Add any future migration scripts here)

echo ===================================================
echo ✅ Setup Complete! Launching App...
echo ===================================================
echo Press Ctrl+C to stop the server.
echo.

streamlit run app.py

pause
