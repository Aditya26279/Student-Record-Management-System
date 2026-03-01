# API Reference — Student Record Management System

## Table of Contents

- [Models](#models)
  - [Student](#student)
  - [Course](#course)
  - [Enrollment](#enrollment)
  - [Attendance / AttendanceSummary](#attendance--attendancesummary)
- [Controllers](#controllers)
  - [StudentController](#studentcontroller)
  - [CourseController](#coursecontroller)
  - [EnrollmentController](#enrollmentcontroller)
  - [AttendanceController](#attendancecontroller)
- [Services](#services)
  - [report\_service](#report_service)
- [Utilities](#utilities)
  - [validators](#validators)
  - [helpers](#helpers)
  - [logger](#logger)
- [Database helpers](#database-helpers)

---

## Models

### Student

```python
from student_management.models import Student
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `student_id` | `Optional[int]` | Primary key (auto) |
| `student_code` | `str` | Auto-generated: `STU{YEAR}{NNNN}` |
| `first_name` | `str` | — |
| `last_name` | `str` | — |
| `date_of_birth` | `Optional[date]` | — |
| `gender` | `str` | `Male` / `Female` / `Other` |
| `email` | `str` | Unique constraint in DB |
| `phone` | `str` | Optional |
| `address` | `str` | Optional |
| `department_id` | `Optional[int]` | FK → departments |
| `department_name` | `str` | Populated via JOIN |
| `enrollment_date` | `Optional[date]` | — |
| `status` | `str` | `active` / `inactive` / `graduated` / `suspended` |
| `gpa` | `float` | Auto-computed by DB trigger |

#### Properties

| Property | Type | Returns |
|---|---|---|
| `full_name` | `str` | `f"{first_name} {last_name}"` |
| `is_active` | `bool` | `True` when `status == "active"` |

#### Methods

| Method | Signature | Description |
|---|---|---|
| `from_row` | `cls, row: dict → Student` | Construct from DB cursor dict |
| `to_dict` | `→ dict` | JSON-serialisable representation |

---

### Course

```python
from student_management.models import Course
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `course_id` | `Optional[int]` | Primary key |
| `course_code` | `str` | Unique (e.g. `CS301`) |
| `course_name` | `str` | — |
| `description` | `str` | — |
| `credits` | `int` | Credit hours |
| `department_id` | `Optional[int]` | FK → departments |
| `department_name` | `str` | Populated via JOIN |
| `semester` | `str` | `"1"`–`"8"` |
| `max_students` | `int` | Seat capacity |
| `is_active` | `bool` | — |
| `enrolled_count` | `int` | From view |
| `avg_marks` | `float` | From view |
| `pass_count` | `int` | From view |
| `fail_count` | `int` | From view |

#### Properties

| Property | Type | Returns |
|---|---|---|
| `seats_available` | `int` | `max_students - enrolled_count` |

---

### Enrollment

```python
from student_management.models import Enrollment, compute_grade
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `enrollment_id` | `Optional[int]` | Primary key |
| `student_id` | `Optional[int]` | FK → students |
| `course_id` | `Optional[int]` | FK → courses |
| `academic_year` | `Optional[int]` | e.g. `2024` |
| `semester` | `str` | `"1"`–`"8"` |
| `internal_marks` | `Optional[float]` | 0–40 |
| `external_marks` | `Optional[float]` | 0–60 |
| `total_marks` | `Optional[float]` | Computed by DB trigger |
| `grade` | `Optional[str]` | `O` / `A+` / `A` / … / `F` |
| `grade_points` | `Optional[float]` | 0.0–10.0 |
| `result` | `Optional[str]` | `Pass` / `Fail` / `Incomplete` |
| `status` | `str` | `enrolled` / `completed` / `dropped` |

#### Properties

| Property | Returns |
|---|---|
| `is_passed` | `True` when `result == "Pass"` |

#### `compute_grade(total: float) → (str, float)`

Returns `(grade_letter, grade_points)` for a raw total marks value.

---

### Attendance / AttendanceSummary

```python
from student_management.models import Attendance, AttendanceSummary
```

**Attendance fields:** `attendance_id`, `student_id`, `course_id`, `attend_date`, `status` (`Present`/`Absent`/`Late`/`OD`), `remarks`, `marked_by`

**AttendanceSummary fields:** `student_id`, `course_id`, `total_classes`, `present_count`, `absent_count`, `late_count`, `attendance_pct`  

**AttendanceSummary.is_eligible** → `True` when `attendance_pct >= 75.0`

---

## Controllers

### StudentController

```python
from student_management.controllers import StudentController
```

| Method | Signature | Returns |
|---|---|---|
| `add` | `(first_name, last_name, dob, gender, email, phone?, address?, department_id?) → Optional[Student]` | New Student or `None` on validation failure |
| `get_by_id` | `(student_id: int) → Optional[Student]` | — |
| `get_by_code` | `(code: str) → Optional[Student]` | — |
| `get_all` | `(status?, department_id?) → List[Student]` | Filtered list |
| `search` | `(keyword: str) → List[Student]` | Matches name / email / code |
| `update` | `(student_id, **kwargs) → bool` | Allowed kwargs: `first_name`, `last_name`, `phone`, `address`, `status`, `department_id`, `gender` |
| `change_status` | `(student_id, status) → bool` | Valid statuses: `active`, `inactive`, `graduated`, `suspended` |
| `delete` | `(student_id) → bool` | Soft-delete: sets status=`inactive` |
| `get_statistics` | `() → dict` | Keys: `total`, `active`, `graduated`, `inactive`, `avg_gpa`, `max_gpa`, `min_gpa` |
| `get_topper` | `(limit=5) → List[Student]` | Descending GPA |
| `get_departments` | `() → List[dict]` | All departments |

---

### CourseController

```python
from student_management.controllers import CourseController
```

| Method | Signature | Returns |
|---|---|---|
| `add` | `(course_code, course_name, credits, semester, department_id?, description?, max_students?) → Optional[Course]` | — |
| `get_by_id` | `(course_id) → Optional[Course]` | — |
| `get_by_code` | `(code) → Optional[Course]` | — |
| `get_all` | `(department_id?, semester?, active_only=True) → List[Course]` | — |
| `get_summary` | `() → List[Course]` | From `vw_course_enrollment_summary` |
| `search` | `(keyword) → List[Course]` | Matches code or name |
| `update` | `(course_id, **kwargs) → bool` | Allowed: `course_name`, `description`, `credits`, `max_students`, `semester`, `department_id`, `is_active` |
| `deactivate` | `(course_id) → bool` | Sets `is_active = False` |
| `get_enrolled_students` | `(course_id, academic_year?, semester?) → List[dict]` | — |

---

### EnrollmentController

```python
from student_management.controllers import EnrollmentController
```

| Method | Signature | Returns |
|---|---|---|
| `enroll` | `(student_id, course_id, academic_year, semester, faculty_id?) → Optional[Enrollment]` | `None` if duplicate |
| `get_by_id` | `(enrollment_id) → Optional[Enrollment]` | — |
| `get_student_enrollments` | `(student_id, academic_year?, semester?) → List[Enrollment]` | — |
| `get_course_enrollments` | `(course_id, academic_year?) → List[Enrollment]` | — |
| `update_marks` | `(enrollment_id, internal_marks, external_marks) → bool` | Validates 0–40 / 0–60 |
| `bulk_update_marks` | `(records: List[dict]) → dict` | `{"success": n, "failed": n}` |
| `drop` | `(enrollment_id) → bool` | Sets status=`dropped` |
| `grade_distribution` | `(course_id, academic_year?) → List[dict]` | Grade, count, % |
| `get_transcript` | `(student_id) → dict` | Keys: `enrollments`, `cgpa`, `total_credits`, `pass_count`, `fail_count` |

---

### AttendanceController

```python
from student_management.controllers import AttendanceController
```

| Method | Signature | Returns |
|---|---|---|
| `mark` | `(student_id, course_id, date, status, marked_by?, remarks?) → bool` | Upserts (ON DUPLICATE KEY) |
| `mark_bulk` | `(course_id, date, records: List[dict], marked_by?) → dict` | `{"success": n, "failed": n}` |
| `get_by_date` | `(course_id, date) → List[Attendance]` | — |
| `get_student_attendance` | `(student_id, course_id?, from_date?, to_date?) → List[Attendance]` | — |
| `get_summary` | `(student_id?, course_id?) → List[AttendanceSummary]` | From `vw_attendance_summary` |
| `get_defaulters` | `(course_id, threshold_pct=75.0) → List[AttendanceSummary]` | Students below threshold |
| `get_course_attendance_dates` | `(course_id) → List[str]` | ISO date strings |

---

## Services

### report\_service

```python
from student_management.services import (
    print_transcript,         # (student_id) → None
    export_transcript_csv,    # (student_id) → Optional[str]  (path)
    print_department_report,  # () → None
    print_defaulters_report,  # (course_id, threshold=75.0) → None
    print_toppers_report,     # (limit=10) → None
    print_grade_distribution, # (course_id, academic_year?) → None
    print_system_summary,     # () → None
)
```

All `print_*` functions write formatted output directly to `stdout`.  
`export_transcript_csv` writes to `reports/transcript_{code}_{ts}.csv` and returns the path.

---

## Utilities

### validators

```python
from student_management.utils.validators import validate_student, validate_marks, ...
```

All validators return `(bool, str)` — `(is_valid, error_message)`.

| Function | Validates |
|---|---|
| `required(value, field_name)` | Not None/empty |
| `max_length(value, field_name, limit)` | String length |
| `is_positive_int(value, field_name)` | Integer > 0 |
| `is_float_range(value, field_name, lo, hi)` | Float in range |
| `validate_email(email)` | RFC-ish email format |
| `validate_phone(phone)` | 7–15 digit phone (optional) |
| `validate_date(value, field_name, fmt)` | Date format |
| `validate_dob(dob_str)` | Date + age 10–100 |
| `validate_choice(value, field_name, choices)` | Enum check |
| `validate_student(data: dict)` | Composite student check |
| `validate_marks(internal, external)` | 0–40 / 0–60 |
| `validate_attendance_status(status)` | Present/Absent/Late/OD |

---

### helpers

```python
from student_management.utils.helpers import print_table, print_success, ...
```

| Function | Description |
|---|---|
| `print_table(rows, headers?, title?)` | Pretty table (uses `tabulate` if installed) |
| `print_header(title)` | Prints a bold coloured header bar |
| `print_success(msg)` | Green ✓ message |
| `print_error(msg)` | Red ✗ message |
| `print_info(msg)` | Blue ℹ message |
| `confirm(prompt) → bool` | y/N prompt |
| `get_input(prompt, default?) → str` | Input with default |
| `get_int_input(prompt, default?) → Optional[int]` | Validated int input |
| `get_float_input(prompt, lo, hi, default?) → Optional[float]` | Validated float input |
| `format_gpa(gpa) → str` | ANSI-coloured GPA string |
| `format_result(result) → str` | Green Pass / Red Fail |
| `format_attendance_pct(pct) → str` | Green ≥75 / Red <75 |
| `today_str() → str` | `YYYY-MM-DD` for today |
| `current_year() → int` | Current calendar year |

---

### logger

```python
from student_management.utils.logger import setup_logger

log = setup_logger("my_module")   # returns logging.Logger
# Writes to console (coloured) AND logs/srms.log (rotating 5 MB)
```

---

## Database helpers

```python
from student_management.config.database import (
    db_session,        # Context manager — auto commit / rollback
    execute_query,     # SELECT → List[dict]
    execute_non_query, # INSERT/UPDATE/DELETE → int (rows affected)
    call_procedure,    # Stored procedure → List[dict]
    test_connection,   # → bool
)
```

### `db_session()` — Context Manager

```python
with db_session() as cur:
    cur.execute("INSERT INTO students (...) VALUES (%s, ...)", (val,))
    new_id = cur.lastrowid
# Transaction committed on success, rolled back on exception
```

### `execute_query(sql, params=()) → List[dict]`

```python
rows = execute_query(
    "SELECT * FROM students WHERE status = %s",
    ("active",)
)
# Returns [] on no results or on error
```

### `execute_non_query(sql, params=()) → int`

```python
affected = execute_non_query(
    "UPDATE students SET phone = %s WHERE student_id = %s",
    ("9999999999", 1)
)
# Returns number of affected rows
```
