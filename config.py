import os
from pathlib import Path

# Project Root
ROOT_DIR = Path(__file__).parent
DATABASE_PATH = os.path.join(ROOT_DIR, 'work_attendance.db')

# Application Settings
APP_NAME = "Work Attendance Tracking System"
VERSION = "1.0.0"
DEBUG = True

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Use env var in production
SESSION_EXPIRY_MINUTES = 60

# Attendance Settings
DEFAULT_WORK_HOURS = 8
DEFAULT_BREAK_DURATION = 60  # minutes

# UI Settings
PAGE_TITLE = "Work Attendance System"
PAGE_ICON = "🏢"
LAYOUT = "wide"
