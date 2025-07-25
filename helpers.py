"""
Helper functions for date and time conversion.

This module provides utility functions for converting between calendar dates
and Python datetime objects.
"""

from datetime import datetime


def cd_to_datetime(calendar_date):
    """
    Convert a calendar date string to a datetime object.
    
    Args:
        calendar_date: A calendar date string in the format "YYYY-MMM-DD HH:MM"
                      where MMM is the three-letter month abbreviation.
    
    Returns:
        A datetime object representing the calendar date.
    """
    # Parse the calendar date string
    # Format: "YYYY-MMM-DD HH:MM" (e.g., "1900-Jan-01 00:00")
    try:
        return datetime.strptime(calendar_date, "%Y-%b-%d %H:%M")
    except ValueError:
        # Try alternative format without time
        try:
            return datetime.strptime(calendar_date, "%Y-%b-%d")
        except ValueError:
            raise ValueError(f"Invalid calendar date format: {calendar_date}")


def datetime_to_str(dt):
    """
    Convert a datetime object to a string representation.
    
    Args:
        dt: A datetime object.
    
    Returns:
        A string representation of the datetime in the format "YYYY-MM-DD HH:MM".
    """
    return dt.strftime("%Y-%m-%d %H:%M") 