"""
tests/unit/test_models.py
Unit tests for data models — Student, Course, Enrollment, Attendance.
No database required — tests from_row(), to_dict(), and computed properties.
"""

import pytest
from student_management.models.student    import Student
from student_management.models.course     import Course
from student_management.models.enrollment import Enrollment, compute_grade
from student_management.models.attendance import Attendance, AttendanceSummary


# ══════════════════════════════════════════════════════════════════════════════
# Student model
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestStudentModel:

    def test_from_row_basic(self, student_row):
        s = Student.from_row(student_row)
        assert s.student_id   == 42
        assert s.student_code == "STU20240042"
        assert s.first_name   == "Aditya"
        assert s.last_name    == "Sharma"
        assert s.gpa          == 8.75
        assert s.status       == "active"
        assert s.department_name == "Computer Science & Engineering"

    def test_full_name_property(self, student_row):
        s = Student.from_row(student_row)
        assert s.full_name == "Aditya Sharma"

    def test_is_active_true(self, student_row):
        s = Student.from_row(student_row)
        assert s.is_active is True

    def test_is_active_false_for_graduated(self, student_row):
        student_row["status"] = "graduated"
        s = Student.from_row(student_row)
        assert s.is_active is False

    def test_to_dict_has_required_keys(self, student_row):
        s   = Student.from_row(student_row)
        d   = s.to_dict()
        for key in ("student_id", "student_code", "full_name", "email",
                    "status", "gpa", "department"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_full_name(self, student_row):
        s = Student.from_row(student_row)
        assert s.to_dict()["full_name"] == "Aditya Sharma"

    def test_gpa_defaults_to_zero_if_none(self):
        s = Student.from_row({"student_id": 1, "gpa": None,
                               "first_name": "X", "last_name": "Y",
                               "status": "active"})
        assert s.gpa == 0.0

    def test_str_representation(self, student_row):
        s   = Student.from_row(student_row)
        rep = str(s)
        assert "Aditya Sharma" in rep
        assert "STU20240042"   in rep
        assert "8.75"          in rep

    def test_default_student_creation(self):
        s = Student()
        assert s.student_id   is None
        assert s.full_name    == " "
        assert s.gpa          == 0.0
        assert s.status       == "active"

    def test_optional_phone_defaults_empty(self):
        s = Student.from_row({"student_id": 1, "phone": None,
                               "first_name": "A", "last_name": "B"})
        assert s.phone == ""


# ══════════════════════════════════════════════════════════════════════════════
# Course model
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestCourseModel:

    def test_from_row_basic(self, course_row):
        c = Course.from_row(course_row)
        assert c.course_id   == 7
        assert c.course_code == "CS301"
        assert c.credits     == 4
        assert c.is_active   is True

    def test_seats_available(self, course_row):
        c = Course.from_row(course_row)
        assert c.seats_available == 60 - 18    # max_students - enrolled_count

    def test_seats_available_full_course(self, course_row):
        course_row["enrolled_count"] = 60
        c = Course.from_row(course_row)
        assert c.seats_available == 0

    def test_to_dict_keys(self, course_row):
        c = Course.from_row(course_row)
        d = c.to_dict()
        for key in ("course_id", "course_code", "course_name",
                    "credits", "semester", "max_students"):
            assert key in d

    def test_str_contains_code_and_name(self, course_row):
        c   = Course.from_row(course_row)
        rep = str(c)
        assert "CS301"           in rep
        assert "Data Structures" in rep

    def test_enrolled_count_defaults_zero(self):
        c = Course.from_row({"course_id": 1, "course_code": "X",
                              "course_name": "Y", "enrolled_count": None})
        assert c.enrolled_count == 0

    def test_stats_from_row(self, course_row):
        c = Course.from_row(course_row)
        assert c.avg_marks  == 72.4
        assert c.pass_count == 16
        assert c.fail_count == 2


# ══════════════════════════════════════════════════════════════════════════════
# Enrollment model
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestEnrollmentModel:

    def test_from_row_basic(self, enrollment_row):
        e = Enrollment.from_row(enrollment_row)
        assert e.enrollment_id  == 99
        assert e.student_code   == "STU20240042"
        assert e.internal_marks == 35.0
        assert e.external_marks == 52.0
        assert e.total_marks    == 87.0
        assert e.grade          == "A+"
        assert e.grade_points   == 9.0
        assert e.result         == "Pass"
        assert e.status         == "completed"

    def test_is_passed_true(self, enrollment_row):
        e = Enrollment.from_row(enrollment_row)
        assert e.is_passed is True

    def test_is_passed_false(self, enrollment_row):
        enrollment_row["result"] = "Fail"
        e = Enrollment.from_row(enrollment_row)
        assert e.is_passed is False

    def test_to_dict_keys(self, enrollment_row):
        e = Enrollment.from_row(enrollment_row)
        d = e.to_dict()
        for key in ("enrollment_id", "student_id", "course_code",
                    "total_marks", "grade", "result"):
            assert key in d

    def test_str_representation(self, enrollment_row):
        e   = Enrollment.from_row(enrollment_row)
        rep = str(e)
        assert "CS301"  in rep
        assert "87.0"   in rep
        assert "Pass"   in rep

    def test_none_marks_handled(self, enrollment_row):
        enrollment_row["internal_marks"] = None
        enrollment_row["external_marks"] = None
        enrollment_row["total_marks"]    = None
        e = Enrollment.from_row(enrollment_row)
        assert e.internal_marks is None
        assert e.total_marks    is None


# ══════════════════════════════════════════════════════════════════════════════
# compute_grade()
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestComputeGrade:
    @pytest.mark.parametrize("total, expected_grade, expected_pts", [
        (95,  "O",   10.0),
        (85,  "A+",   9.0),
        (75,  "A",    8.0),
        (65,  "B+",   7.0),
        (55,  "B",    6.0),
        (45,  "C",    5.0),
        (39,  "F",    0.0),
        (0,   "F",    0.0),
        (100, "O",   10.0),
        (90,  "O",   10.0),
        (80,  "A+",   9.0),
    ])
    def test_grade_thresholds(self, total, expected_grade, expected_pts):
        grade, pts = compute_grade(total)
        assert grade == expected_grade, f"total={total}: expected {expected_grade}, got {grade}"
        assert pts   == expected_pts


# ══════════════════════════════════════════════════════════════════════════════
# Attendance model
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestAttendanceModel:

    def test_from_row_basic(self, attendance_row):
        a = Attendance.from_row(attendance_row)
        assert a.attendance_id == 200
        assert a.student_code  == "STU20240042"
        assert a.status        == "Present"
        assert a.course_code   == "CS301"

    def test_to_dict_keys(self, attendance_row):
        a = Attendance.from_row(attendance_row)
        d = a.to_dict()
        for key in ("attendance_id", "student_id", "status", "attend_date"):
            assert key in d

    def test_str_representation(self, attendance_row):
        a   = Attendance.from_row(attendance_row)
        rep = str(a)
        assert "Aditya Sharma" in rep
        assert "Present"       in rep

    def test_remarks_defaults_empty_for_none(self, attendance_row):
        attendance_row["remarks"] = None
        a = Attendance.from_row(attendance_row)
        assert a.remarks == ""


# ══════════════════════════════════════════════════════════════════════════════
# AttendanceSummary model
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.unit
class TestAttendanceSummaryModel:

    def test_from_row_basic(self, attendance_summary_row):
        s = AttendanceSummary.from_row(attendance_summary_row)
        assert s.total_classes  == 40
        assert s.present_count  == 32
        assert s.attendance_pct == 80.0

    def test_is_eligible_above_threshold(self, attendance_summary_row):
        s = AttendanceSummary.from_row(attendance_summary_row)
        assert s.is_eligible is True   # 80% >= 75%

    def test_is_eligible_exactly_at_threshold(self, attendance_summary_row):
        attendance_summary_row["attendance_pct"] = 75.0
        s = AttendanceSummary.from_row(attendance_summary_row)
        assert s.is_eligible is True

    def test_is_not_eligible_below_threshold(self, attendance_summary_row):
        attendance_summary_row["attendance_pct"] = 74.9
        s = AttendanceSummary.from_row(attendance_summary_row)
        assert s.is_eligible is False

    def test_str_shows_eligibility(self, attendance_summary_row):
        s   = AttendanceSummary.from_row(attendance_summary_row)
        rep = str(s)
        assert "CS301"   in rep
        assert "80.0%"   in rep
        assert "Eligible" in rep

    def test_zero_total_classes(self):
        s = AttendanceSummary.from_row({
            "total_classes": 0, "present_count": 0,
            "attendance_pct": 0.0,
        })
        assert s.is_eligible is False
        assert s.total_classes == 0
