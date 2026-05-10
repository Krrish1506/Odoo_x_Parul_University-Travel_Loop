"""
validators.py — Centralized input validation with clear error messages.
All user input must pass through these validators before DB operations.
"""
import re

# ── Compiled regex patterns (performance) ─────────────────────────────
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_MIN = 6


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format. Returns (is_valid, error_message)."""
    if not email or not email.strip():
        return False, "Email address is required."
    email = email.strip()
    if len(email) > 255:
        return False, "Email address is too long (max 255 characters)."
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address (e.g. user@example.com)."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength. Returns (is_valid, error_message)."""
    if not password:
        return False, "Password is required."
    if len(password) < PASSWORD_MIN:
        return False, f"Password must be at least {PASSWORD_MIN} characters."
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    return True, ""


def validate_name(name: str) -> tuple[bool, str]:
    """Validate user display name. Returns (is_valid, error_message)."""
    if not name or not name.strip():
        return False, "Name is required."
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters."
    if len(name) > 50:
        return False, "Name must be under 50 characters."
    if not re.match(r'^[a-zA-Z\s\'-]+$', name):
        return False, "Name can only contain letters, spaces, hyphens, and apostrophes."
    return True, ""


def validate_trip_name(name: str) -> tuple[bool, str]:
    """Validate trip name. Returns (is_valid, error_message)."""
    if not name or not name.strip():
        return False, "Trip name is required."
    if len(name.strip()) > 100:
        return False, "Trip name must be under 100 characters."
    return True, ""


def validate_date_range(start: str, end: str) -> tuple[bool, str]:
    """Validate that start_date <= end_date and both are present."""
    if not start:
        return False, "Start date is required."
    if not end:
        return False, "End date is required."
    if start > end:
        return False, "Start date cannot be after end date."
    return True, ""


def validate_positive_number(value, field_name: str = "Value") -> tuple[bool, str]:
    """Validate that a number is non-negative."""
    try:
        num = float(value) if value else 0
        if num < 0:
            return False, f"{field_name} cannot be negative."
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number."


def validate_num_days(days) -> tuple[bool, str]:
    """Validate number of days for a stop."""
    try:
        d = int(days) if days else 0
        if d < 1:
            return False, "Must stay at least 1 day."
        if d > 30:
            return False, "Maximum 30 days per stop."
        return True, ""
    except (ValueError, TypeError):
        return False, "Days must be a valid number."


def sanitize_string(text: str, max_length: int = 500) -> str:
    """Strip whitespace and truncate to max length for safety."""
    if not text:
        return ""
    return text.strip()[:max_length]
