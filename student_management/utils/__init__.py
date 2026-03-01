# student_management/utils/__init__.py
from .logger     import setup_logger, log
from .validators import (validate_student, validate_marks,
                          validate_email, validate_phone,
                          validate_attendance_status, validate_date)
from .helpers    import (print_table, print_header, print_success,
                          print_error, print_info, confirm,
                          get_input, get_int_input, get_float_input,
                          format_gpa, format_result, format_attendance_pct,
                          today_str, current_year)

__all__ = [
    "setup_logger", "log",
    "validate_student", "validate_marks", "validate_email",
    "validate_phone", "validate_attendance_status", "validate_date",
    "print_table", "print_header", "print_success", "print_error",
    "print_info", "confirm", "get_input", "get_int_input", "get_float_input",
    "format_gpa", "format_result", "format_attendance_pct",
    "today_str", "current_year",
]
