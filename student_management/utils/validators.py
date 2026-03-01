"""
utils/validators.py — Input validation for all SRMS entities
Returns (is_valid: bool, error_message: str)
"""

import re
from datetime import date, datetime
from typing import Tuple

ValidResult = Tuple[bool, str]


# ── Generic ──────────────────────────────────────────────────────────────── #

def required(value, field_name: str) -> ValidResult:
    if value is None or str(value).strip() == "":
        return False, f"{field_name} is required."
    return True, ""


def max_length(value: str, field_name: str, limit: int) -> ValidResult:
    if len(str(value)) > limit:
        return False, f"{field_name} must be at most {limit} characters."
    return True, ""


def is_positive_int(value, field_name: str) -> ValidResult:
    try:
        v = int(value)
        if v <= 0:
            raise ValueError
        return True, ""
    except (TypeError, ValueError):
        return False, f"{field_name} must be a positive integer."


def is_float_range(value, field_name: str, lo: float, hi: float) -> ValidResult:
    try:
        v = float(value)
        if not lo <= v <= hi:
            return False, f"{field_name} must be between {lo} and {hi}."
        return True, ""
    except (TypeError, ValueError):
        return False, f"{field_name} must be a number."


# ── Email ────────────────────────────────────────────────────────────────── #
_EMAIL_RE = re.compile(r"^[\w.+\-]+@[\w\-]+(\.[\w\-]+)*\.[a-z]{2,}$", re.IGNORECASE)

def validate_email(email: str) -> ValidResult:
    ok, msg = required(email, "Email")
    if not ok:
        return ok, msg
    if not _EMAIL_RE.match(email.strip()):
        return False, "Invalid email format."
    return True, ""


# ── Phone ────────────────────────────────────────────────────────────────── #
_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,15}$")

def validate_phone(phone: str) -> ValidResult:
    if not phone:
        return True, ""          # phone is optional
    if not _PHONE_RE.match(phone.strip()):
        return False, "Phone must be 7-15 digits (spaces/dashes/parens allowed)."
    return True, ""


# ── Date ─────────────────────────────────────────────────────────────────── #

def validate_date(value: str, field_name: str = "Date",
                   fmt: str = "%Y-%m-%d") -> ValidResult:
    ok, msg = required(value, field_name)
    if not ok:
        return ok, msg
    try:
        datetime.strptime(str(value), fmt)
        return True, ""
    except ValueError:
        return False, f"{field_name} must be in {fmt} format."


def validate_dob(dob_str: str) -> ValidResult:
    ok, msg = validate_date(dob_str, "Date of Birth")
    if not ok:
        return ok, msg
    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    today = date.today()
    age   = (today - dob).days // 365
    if age < 10 or age > 100:
        return False, "Date of Birth implies an unreasonable age."
    return True, ""


# ── Enums ────────────────────────────────────────────────────────────────── #

def validate_choice(value: str, field_name: str, choices: tuple) -> ValidResult:
    if value not in choices:
        return False, f"{field_name} must be one of: {', '.join(choices)}."
    return True, ""


# ── Student ──────────────────────────────────────────────────────────────── #

def validate_student(data: dict) -> ValidResult:
    """Validate all required fields for creating/updating a student."""
    checks = [
        required(data.get("first_name"), "First Name"),
        required(data.get("last_name"),  "Last Name"),
        validate_email(data.get("email", "")),
        validate_dob(str(data.get("date_of_birth", ""))),
        validate_choice(data.get("gender", ""), "Gender",
                        ("Male", "Female", "Other")),
        validate_phone(data.get("phone", "")),
        max_length(data.get("first_name", ""), "First Name", 50),
        max_length(data.get("last_name",  ""), "Last Name",  50),
    ]
    for ok, msg in checks:
        if not ok:
            return False, msg
    return True, ""


# ── Marks ────────────────────────────────────────────────────────────────── #

def validate_marks(internal, external) -> ValidResult:
    ok, msg = is_float_range(internal, "Internal Marks", 0, 40)
    if not ok:
        return ok, msg
    ok, msg = is_float_range(external, "External Marks", 0, 60)
    return ok, msg


# ── Attendance ───────────────────────────────────────────────────────────── #

def validate_attendance_status(status: str) -> ValidResult:
    return validate_choice(status, "Attendance Status",
                           ("Present", "Absent", "Late", "OD"))
