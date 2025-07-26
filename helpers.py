"""
Miscellaneous helper functions for the NEO Explorer.

This module provides utility functions for date/time conversion and other
helpers.
"""

from datetime import datetime


def cd_to_datetime(calendar_date):
    """
    Convert a NASA JPL calendar date string to a datetime object.

    NASA JPL calendar dates are formatted as strings like "2000-Jan-01 12:00".

    Args:
        calendar_date: A calendar date string from NASA JPL.

    Returns:
        A datetime object corresponding to the given calendar date.

    Raises:
        ValueError: If the calendar date format is invalid.
    """
    try:
        # Parse the date string in the expected format
        return datetime.strptime(calendar_date, "%Y-%b-%d %H:%M")
    except ValueError as exc:
        # Re-raise with more context
        raise ValueError(f"Invalid calendar date format: "
                         f"{calendar_date}") from exc


def datetime_to_str(dt):
    """
    Convert a datetime object to a formatted string.

    Args:
        dt: A datetime object.

    Returns:
        A formatted string representation of the datetime.
    """
    return dt.strftime("%Y-%m-%d %H:%M")
