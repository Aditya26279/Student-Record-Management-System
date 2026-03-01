"""
tests/unit/test_validators.py
Unit tests for student_management.utils.validators
No database required — pure Python logic.
"""

import pytest
from student_management.utils.validators import (
    required, max_length, is_positive_int, is_float_range,
    validate_email, validate_phone, validate_date, validate_dob,
    validate_choice, validate_student, validate_marks,
    validate_attendance_status,
)


# ══════════════════════════════════════════════════════════════════════════════
# required()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestRequired:
    def test_valid_string(self):
        ok, msg = required("hello", "Field")
        assert ok is True
        assert msg == ""

    def test_none_fails(self):
        ok, msg = required(None, "Field")
        assert ok is False
        assert "required" in msg.lower()

    def test_empty_string_fails(self):
        ok, msg = required("", "Field")
        assert ok is False

    def test_whitespace_only_fails(self):
        ok, msg = required("   ", "Field")
        assert ok is False

    def test_zero_is_valid(self):
        ok, _ = required(0, "Field")
        assert ok is True            # 0 is not None/empty


# ══════════════════════════════════════════════════════════════════════════════
# max_length()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestMaxLength:
    def test_within_limit(self):
        ok, _ = max_length("hello", "Field", 10)
        assert ok is True

    def test_exactly_at_limit(self):
        ok, _ = max_length("a" * 10, "Field", 10)
        assert ok is True

    def test_exceeds_limit(self):
        ok, msg = max_length("a" * 11, "Field", 10)
        assert ok is False
        assert "10" in msg


# ══════════════════════════════════════════════════════════════════════════════
# is_positive_int()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestIsPositiveInt:
    @pytest.mark.parametrize("v", [1, 42, 1000, "7"])
    def test_valid(self, v):
        ok, _ = is_positive_int(v, "F")
        assert ok is True

    @pytest.mark.parametrize("v", [0, -1, -99, "abc", None])
    def test_invalid(self, v):
        ok, _ = is_positive_int(v, "F")
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# is_float_range()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestIsFloatRange:
    def test_within_range(self):
        ok, _ = is_float_range(50, "Marks", 0, 100)
        assert ok is True

    def test_lower_bound(self):
        ok, _ = is_float_range(0, "Marks", 0, 100)
        assert ok is True

    def test_upper_bound(self):
        ok, _ = is_float_range(100, "Marks", 0, 100)
        assert ok is True

    def test_below_range(self):
        ok, _ = is_float_range(-1, "Marks", 0, 100)
        assert ok is False

    def test_above_range(self):
        ok, _ = is_float_range(101, "Marks", 0, 100)
        assert ok is False

    def test_non_numeric_fails(self):
        ok, _ = is_float_range("abc", "Marks", 0, 100)
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_email()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateEmail:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test.user+tag@sub.domain.org",
        "a@b.io",
    ])
    def test_valid_emails(self, email):
        ok, _ = validate_email(email)
        assert ok is True

    @pytest.mark.parametrize("email", [
        "",
        "notanemail",
        "missing@dot",
        "@nodomain.com",
        "spaces in@email.com",
    ])
    def test_invalid_emails(self, email):
        ok, _ = validate_email(email)
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_phone()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidatePhone:
    def test_empty_phone_is_ok(self):
        """Phone is optional."""
        ok, _ = validate_phone("")
        assert ok is True

    @pytest.mark.parametrize("phone", [
        "9876543210",
        "+91 98765 43210",
        "(040) 2345-6789",
    ])
    def test_valid_phones(self, phone):
        ok, _ = validate_phone(phone)
        assert ok is True

    @pytest.mark.parametrize("phone", [
        "123",              # too short
        "abcdefghi",        # non-numeric
        "123456789012345678",  # too long
    ])
    def test_invalid_phones(self, phone):
        ok, _ = validate_phone(phone)
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_date()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateDate:
    def test_valid_date(self):
        ok, _ = validate_date("2024-01-15")
        assert ok is True

    def test_wrong_format(self):
        ok, _ = validate_date("15-01-2024")
        assert ok is False

    def test_empty(self):
        ok, _ = validate_date("")
        assert ok is False

    def test_invalid_day(self):
        ok, _ = validate_date("2024-02-30")    # Feb 30 doesn't exist
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_dob()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateDob:
    def test_reasonable_age(self):
        ok, _ = validate_dob("2002-06-15")
        assert ok is True

    def test_future_date_fails(self):
        ok, _ = validate_dob("2099-01-01")
        assert ok is False

    def test_too_old_fails(self):
        ok, _ = validate_dob("1900-01-01")
        assert ok is False

    def test_wrong_format(self):
        ok, _ = validate_dob("15/06/2002")
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_choice()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateChoice:
    GENDERS = ("Male", "Female", "Other")

    def test_valid_choice(self):
        ok, _ = validate_choice("Male", "Gender", self.GENDERS)
        assert ok is True

    def test_invalid_choice(self):
        ok, _ = validate_choice("Unknown", "Gender", self.GENDERS)
        assert ok is False

    def test_case_sensitive(self):
        ok, _ = validate_choice("male", "Gender", self.GENDERS)
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_student()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateStudent:
    def test_full_valid_student(self, valid_student_dict):
        ok, msg = validate_student(valid_student_dict)
        assert ok is True, f"Expected valid, got: {msg}"

    def test_missing_first_name(self, valid_student_dict):
        valid_student_dict["first_name"] = ""
        ok, _ = validate_student(valid_student_dict)
        assert ok is False

    def test_missing_last_name(self, valid_student_dict):
        valid_student_dict["last_name"] = ""
        ok, _ = validate_student(valid_student_dict)
        assert ok is False

    def test_bad_email(self, valid_student_dict):
        valid_student_dict["email"] = "notvalid"
        ok, _ = validate_student(valid_student_dict)
        assert ok is False

    def test_invalid_dob(self, valid_student_dict):
        valid_student_dict["date_of_birth"] = "not-a-date"
        ok, _ = validate_student(valid_student_dict)
        assert ok is False

    def test_invalid_gender(self, valid_student_dict):
        valid_student_dict["gender"] = "Robot"
        ok, _ = validate_student(valid_student_dict)
        assert ok is False

    def test_first_name_too_long(self, valid_student_dict):
        valid_student_dict["first_name"] = "A" * 51
        ok, _ = validate_student(valid_student_dict)
        assert ok is False

    def test_optional_phone_is_allowed_empty(self, valid_student_dict):
        valid_student_dict["phone"] = ""
        ok, msg = validate_student(valid_student_dict)
        assert ok is True


# ══════════════════════════════════════════════════════════════════════════════
# validate_marks()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateMarks:
    def test_valid_marks(self):
        ok, _ = validate_marks(35, 55)
        assert ok is True

    def test_zero_marks_valid(self):
        ok, _ = validate_marks(0, 0)
        assert ok is True

    def test_full_marks_valid(self):
        ok, _ = validate_marks(40, 60)
        assert ok is True

    def test_internal_too_high(self):
        ok, _ = validate_marks(41, 50)
        assert ok is False

    def test_external_too_high(self):
        ok, _ = validate_marks(30, 61)
        assert ok is False

    def test_negative_marks(self):
        ok, _ = validate_marks(-1, 50)
        assert ok is False

    def test_non_numeric(self):
        ok, _ = validate_marks("abc", 50)
        assert ok is False


# ══════════════════════════════════════════════════════════════════════════════
# validate_attendance_status()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestValidateAttendanceStatus:
    @pytest.mark.parametrize("status", ["Present", "Absent", "Late", "OD"])
    def test_valid_statuses(self, status):
        ok, _ = validate_attendance_status(status)
        assert ok is True

    @pytest.mark.parametrize("status", ["present", "P", "absent", "", "Holiday"])
    def test_invalid_statuses(self, status):
        ok, _ = validate_attendance_status(status)
        assert ok is False
