from datetime import datetime, timedelta
import math
from config import DEFAULT_WORK_HOURS

def calculate_time_difference(start_time, end_time):
    """Calculate difference in hours between two datetime objects"""
    if not start_time or not end_time:
        return 0.0
    
    if isinstance(start_time, str):
        # Handle string inputs if necessary, though datetime objects preferred
        pass

    diff = end_time - start_time
    hours = diff.total_seconds() / 3600
    return round(bytes_to_float=hours, ndigits=2)

def calculate_work_hours(clock_in, clock_out, break_duration_minutes=60):
    """
    Calculate total and regular hours.
    Returns: (total_hours, regular_hours, overtime_hours)
    """
    if not clock_in or not clock_out:
        return 0.0, 0.0, 0.0
        
    duration = clock_out - clock_in
    total_hours_raw = duration.total_seconds() / 3600
    
    # Subtract break
    break_hours = break_duration_minutes / 60
    actual_work_hours = max(0.0, total_hours_raw - break_hours)
    
    regular_hours = min(actual_work_hours, DEFAULT_WORK_HOURS)
    overtime_hours = max(0.0, actual_work_hours - DEFAULT_WORK_HOURS)
    
    return (
        round(actual_work_hours, 2),
        round(regular_hours, 2),
        round(overtime_hours, 2)
    )

def calculate_salary(hourly_rate, regular_hours, overtime_hours, overtime_rate_multiplier=1.5):
    """Calculate salary based on hours and rates"""
    regular_pay = regular_hours * hourly_rate
    overtime_pay = overtime_hours * hourly_rate * overtime_rate_multiplier
    return round(regular_pay + overtime_pay, 2)
