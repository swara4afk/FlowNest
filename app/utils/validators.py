"""
Lightweight form validation helpers.

Kept framework-free (no external form library) so the auth module
stays dependency-light and easy to read for portfolio reviewers.
"""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def is_valid_password(password: str) -> bool:
    """Minimum viable rule for a portfolio project: at least 6 characters."""
    return bool(password) and len(password) >= 6


def validate_registration(full_name: str, email: str, password: str, confirm_password: str) -> list[str]:
    errors = []

    if not full_name or len(full_name.strip()) < 2:
        errors.append("Please enter your full name.")

    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")

    if not is_valid_password(password):
        errors.append("Password must be at least 6 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors
