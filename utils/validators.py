import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (basic validation)"""
    if not phone:
        return True # Optional field
    # Allow digits, spaces, dashes, plus, parentheses
    pattern = r'^[\d\s\-\+\(\)]+$'
    return re.match(pattern, phone) is not None

def validate_date_range(start_date, end_date):
    """Validate start date is before or equal to end date"""
    if not start_date or not end_date:
        return False
    return start_date <= end_date

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    return text.strip()
