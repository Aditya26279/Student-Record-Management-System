"""
tests/integration/test_attendance_controller.py
Integration tests for AttendanceController — requires live DB.
"""

import pytest
from student_management.controllers.attendance_controller import AttendanceController
from student_management.config.database import execute_non_query


pytestmark = pytest.mark.integration


# ── Helpers ──────────────────────────────────────────────────────────────────

TEST_DATE  = "2099-11-15"   # Far-future date unlikely to conflict with seed data
TEST_DATE2 = "2099-11-16"


def _cleanup_attendance(student_id: int, course_id: int) -> None:
    execute_non_query(
        "DELETE FROM attendance WHERE student_id = %s AND course_id = %s "
        "AND attend_date >= '2099-01-01'",
        (student_id, course_id),
    )


# ══════════════════════════════════════════════════════════════════════════════
# Read-only tests
# ══════════════════════════════════════════════════════════════════════════════
class TestAttendanceControllerRead:

    def test_get_summary_returns_list(self, require_db):
        summaries = AttendanceController.get_summary()
        assert isinstance(summaries, list)

    def test_get_summary_by_student(self, require_db):
        from student_management.controllers.student_controller import StudentController
        students = StudentController.get_all()
        if not students:
            pytest.skip("No students")
        s = students[0]
        summaries = AttendanceController.get_summary(student_id=s.student_id)
        assert all(sm.student_id == s.student_id for sm in summaries)

    def test_get_summary_by_course(self, require_db):
        from student_management.controllers.course_controller import CourseController
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses")
        c = courses[0]
        summaries = AttendanceController.get_summary(course_id=c.course_id)
        assert all(sm.course_id == c.course_id for sm in summaries)

    def test_get_defaulters_returns_list(self, require_db):
        from student_management.controllers.course_controller import CourseController
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses")
        defaulters = AttendanceController.get_defaulters(courses[0].course_id, 75.0)
        assert isinstance(defaulters, list)

    def test_defaulters_all_below_threshold(self, require_db):
        from student_management.controllers.course_controller import CourseController
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses")
        threshold  = 75.0
        defaulters = AttendanceController.get_defaulters(courses[0].course_id, threshold)
        assert all(d.attendance_pct < threshold for d in defaulters)

    def test_get_course_attendance_dates_returns_list(self, require_db):
        from student_management.controllers.course_controller import CourseController
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses")
        dates = AttendanceController.get_course_attendance_dates(courses[0].course_id)
        assert isinstance(dates, list)

    def test_get_student_attendance(self, require_db):
        from student_management.controllers.student_controller import StudentController
        students = StudentController.get_all()
        if not students:
            pytest.skip("No students")
        records = AttendanceController.get_student_attendance(students[0].student_id)
        assert isinstance(records, list)


# ══════════════════════════════════════════════════════════════════════════════
# Write tests (mark / bulk)
# ══════════════════════════════════════════════════════════════════════════════
class TestAttendanceControllerWrite:

    def test_mark_present_succeeds(self, test_student, test_course, test_enrollment):
        ok = AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Present",
        )
        assert ok is True
        _cleanup_attendance(test_student.student_id, test_course.course_id)

    def test_mark_absent_succeeds(self, test_student, test_course, test_enrollment):
        ok = AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Absent",
        )
        assert ok is True
        _cleanup_attendance(test_student.student_id, test_course.course_id)

    @pytest.mark.parametrize("status", ["Present", "Absent", "Late", "OD"])
    def test_all_valid_statuses(self, status, test_student, test_course, test_enrollment):
        ok = AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, status,
        )
        assert ok is True
        _cleanup_attendance(test_student.student_id, test_course.course_id)

    def test_invalid_status_fails(self, test_student, test_course, test_enrollment):
        ok = AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Holiday",
        )
        assert ok is False

    def test_invalid_date_fails(self, test_student, test_course, test_enrollment):
        ok = AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            "not-a-date", "Present",
        )
        assert ok is False

    def test_upsert_overwrites_existing(self, test_student, test_course, test_enrollment):
        """Marking twice on the same date should upsert (ON DUPLICATE KEY UPDATE)."""
        AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Present",
        )
        AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Absent",   # overwrite
        )
        records = AttendanceController.get_by_date(test_course.course_id, TEST_DATE)
        student_rec = [r for r in records
                       if r.student_id == test_student.student_id]
        assert len(student_rec) == 1
        assert student_rec[0].status == "Absent"
        _cleanup_attendance(test_student.student_id, test_course.course_id)

    def test_get_by_date_returns_marked_records(self, test_student, test_course, test_enrollment):
        AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Present",
        )
        records = AttendanceController.get_by_date(test_course.course_id, TEST_DATE)
        assert any(r.student_id == test_student.student_id for r in records)
        _cleanup_attendance(test_student.student_id, test_course.course_id)

    def test_get_by_date_empty_for_no_records(self, test_student, test_course, test_enrollment):
        records = AttendanceController.get_by_date(test_course.course_id, "2088-01-01")
        assert records == []

    def test_bulk_mark_success(self, test_student, test_course, test_enrollment):
        records = [
            {"student_id": test_student.student_id, "status": "Present", "remarks": ""},
        ]
        result = AttendanceController.mark_bulk(
            test_course.course_id, TEST_DATE, records,
        )
        assert result["success"] == 1
        assert result["failed"]  == 0
        _cleanup_attendance(test_student.student_id, test_course.course_id)

    def test_bulk_mark_invalid_date(self, test_student, test_course, test_enrollment):
        records = [{"student_id": test_student.student_id, "status": "Present"}]
        result  = AttendanceController.mark_bulk(
            test_course.course_id, "bad-date", records,
        )
        assert result["success"] == 0
        assert result["failed"]  == 1

    def test_student_attendance_filter_by_date_range(
            self, test_student, test_course, test_enrollment):
        AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE, "Present",
        )
        AttendanceController.mark(
            test_student.student_id, test_course.course_id,
            TEST_DATE2, "Late",
        )
        records = AttendanceController.get_student_attendance(
            test_student.student_id,
            course_id=test_course.course_id,
            from_date="2099-01-01",
            to_date="2099-12-31",
        )
        dates_recorded = {r.attend_date for r in records}
        assert TEST_DATE  in dates_recorded
        assert TEST_DATE2 in dates_recorded
        _cleanup_attendance(test_student.student_id, test_course.course_id)
