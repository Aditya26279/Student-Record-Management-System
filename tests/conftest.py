"""
tests/conftest.py — Shared pytest fixtures for the full test suite.

Unit tests use the lightweight fixtures (no DB).
Integration tests use the DB-backed fixtures which create isolated
test records and clean them up in teardown.
"""

import os
import sys
import pytest

# ── Ensure project root is importable ────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Default DB env so integration tests can reach the DB ─────────────────────
os.environ.setdefault("DB_USER",     "root")
os.environ.setdefault("DB_HOST",     "localhost")
os.environ.setdefault("DB_NAME",     "student_management_db")
os.environ.setdefault("DB_PASSWORD", "12345")


# ═════════════════════════════════════════════════════════════════════════════
# UNIT FIXTURES  (no database — plain Python dicts / dataclasses)
# ═════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def valid_student_dict():
    return {
        "first_name":   "Test",
        "last_name":    "User",
        "date_of_birth":"2000-06-15",
        "gender":       "Male",
        "email":        "test.user@example.com",
        "phone":        "9876543210",
        "address":      "123 Test Street",
    }


@pytest.fixture
def student_row():
    """Simulated DB row dict for Student.from_row()."""
    return {
        "student_id":    42,
        "student_code":  "STU20240042",
        "first_name":    "Aditya",
        "last_name":     "Sharma",
        "date_of_birth": "2002-03-10",
        "gender":        "Male",
        "email":         "aditya@example.com",
        "phone":         "9988776655",
        "address":       "Pune, Maharashtra",
        "department_id": 1,
        "dept_name":     "Computer Science & Engineering",
        "enrollment_date":"2024-08-01",
        "status":        "active",
        "gpa":           8.75,
    }


@pytest.fixture
def course_row():
    return {
        "course_id":      7,
        "course_code":    "CS301",
        "course_name":    "Data Structures",
        "description":    "Linked lists, trees, graphs.",
        "credits":        4,
        "department_id":  1,
        "dept_name":      "Computer Science & Engineering",
        "semester":       "3",
        "max_students":   60,
        "is_active":      True,
        "enrolled_count": 18,
        "avg_marks":      72.4,
        "pass_count":     16,
        "fail_count":     2,
    }


@pytest.fixture
def enrollment_row():
    return {
        "enrollment_id":  99,
        "student_id":     42,
        "student_name":   "Aditya Sharma",
        "student_code":   "STU20240042",
        "course_id":      7,
        "course_code":    "CS301",
        "course_name":    "Data Structures",
        "faculty_id":     2,
        "academic_year":  2024,
        "semester":       "3",
        "internal_marks": 35.0,
        "external_marks": 52.0,
        "total_marks":    87.0,
        "grade":          "A+",
        "grade_points":   9.0,
        "result":         "Pass",
        "enrollment_date":"2024-08-01",
        "status":         "completed",
    }


@pytest.fixture
def attendance_row():
    return {
        "attendance_id": 200,
        "student_id":    42,
        "student_name":  "Aditya Sharma",
        "student_code":  "STU20240042",
        "course_id":     7,
        "course_code":   "CS301",
        "course_name":   "Data Structures",
        "attend_date":   "2024-09-15",
        "status":        "Present",
        "remarks":       "",
        "marked_by":     3,
    }


@pytest.fixture
def attendance_summary_row():
    return {
        "student_id":     42,
        "student_code":   "STU20240042",
        "student_name":   "Aditya Sharma",
        "course_id":      7,
        "course_code":    "CS301",
        "course_name":    "Data Structures",
        "total_classes":  40,
        "present_count":  32,
        "absent_count":   6,
        "late_count":     2,
        "attendance_pct": 80.0,
    }


# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION FIXTURES  (DB-backed; skip if DB unreachable)
# ═════════════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Register custom markers to avoid PytestUnknownMarkWarning."""
    config.addinivalue_line("markers", "unit: fast no-DB unit tests")
    config.addinivalue_line("markers", "integration: tests that need a live DB")


@pytest.fixture(scope="session")
def db_available():
    """Session-scoped check: skip all integration tests if DB is down."""
    from student_management.config.database import test_connection
    return test_connection()


@pytest.fixture(scope="session")
def require_db(db_available):
    if not db_available:
        pytest.skip("No database connection — skipping integration tests")
    return True


# ── Test department ID (CS dept from seed data) ───────────────────────────────
@pytest.fixture(scope="session")
def cs_dept_id(require_db):
    from student_management.config.database import execute_query
    rows = execute_query(
        "SELECT department_id FROM departments WHERE dept_code = 'CS' LIMIT 1"
    )
    return rows[0]["department_id"] if rows else 1


# ── One-shot test student (created & destroyed per test module) ───────────────
@pytest.fixture
def test_student(require_db, cs_dept_id):
    """Create a disposable student, yield it, then delete it."""
    from student_management.controllers.student_controller import StudentController
    from student_management.config.database import execute_non_query

    import random
    tag = random.randint(10000, 99999)
    s   = StudentController.add(
        first_name=   "PytestFirst",
        last_name=    f"PytestLast{tag}",
        dob=          "2002-01-01",
        gender=       "Male",
        email=        f"pytest_{tag}@test.local",
        phone=        "9000000000",
        address=      "Test Avenue",
        department_id=cs_dept_id,
    )
    assert s is not None, "Fixture: failed to create test student"
    yield s

    # Teardown — hard delete so the DB stays clean
    execute_non_query(
        "DELETE FROM students WHERE student_id = %s", (s.student_id,)
    )


# ── One-shot test course ──────────────────────────────────────────────────────
@pytest.fixture
def test_course(require_db, cs_dept_id):
    """Create a disposable course, yield it, then delete it."""
    from student_management.controllers.course_controller import CourseController
    from student_management.config.database import execute_non_query

    import random
    tag = random.randint(10000, 99999)
    c   = CourseController.add(
        course_code=  f"TST{tag}",
        course_name=  f"Pytest Course {tag}",
        credits=      3,
        semester=     "1",
        department_id=cs_dept_id,
        max_students= 30,
    )
    assert c is not None, "Fixture: failed to create test course"
    yield c

    execute_non_query(
        "DELETE FROM courses WHERE course_id = %s", (c.course_id,)
    )


# ── One-shot test enrollment ──────────────────────────────────────────────────
@pytest.fixture
def test_enrollment(require_db, test_student, test_course):
    """Enroll test_student in test_course, yield the Enrollment, then clean up."""
    from student_management.controllers.enrollment_controller import EnrollmentController
    from student_management.config.database import execute_non_query

    e = EnrollmentController.enroll(
        student_id=   test_student.student_id,
        course_id=    test_course.course_id,
        academic_year=2099,       # far-future year keeps it isolated
        semester=     "1",
    )
    assert e is not None, "Fixture: failed to create test enrollment"
    yield e

    execute_non_query(
        "DELETE FROM enrollments WHERE enrollment_id = %s", (e.enrollment_id,)
    )
