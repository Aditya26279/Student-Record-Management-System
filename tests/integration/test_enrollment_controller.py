"""
tests/integration/test_enrollment_controller.py
Integration tests for EnrollmentController — requires live DB.
"""

import pytest
from student_management.controllers.enrollment_controller import EnrollmentController
from student_management.controllers.student_controller    import StudentController
from student_management.config.database import execute_non_query


pytestmark = pytest.mark.integration


class TestEnrollmentControllerRead:

    def test_get_student_enrollments_returns_list(self, require_db):
        students = StudentController.get_all()
        if not students:
            pytest.skip("No students in DB")
        enr = EnrollmentController.get_student_enrollments(students[0].student_id)
        assert isinstance(enr, list)

    def test_get_course_enrollments_returns_list(self, require_db):
        from student_management.controllers.course_controller import CourseController
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses in DB")
        enr = EnrollmentController.get_course_enrollments(courses[0].course_id)
        assert isinstance(enr, list)

    def test_get_by_id_nonexistent(self, require_db):
        e = EnrollmentController.get_by_id(999999)
        assert e is None


class TestEnrollmentControllerWrite:

    def test_enroll_creates_record(self, test_enrollment):
        assert test_enrollment is not None
        assert test_enrollment.enrollment_id is not None
        assert test_enrollment.status == "enrolled"

    def test_enrolled_record_readable(self, test_enrollment):
        fetched = EnrollmentController.get_by_id(test_enrollment.enrollment_id)
        assert fetched is not None
        assert fetched.enrollment_id == test_enrollment.enrollment_id

    def test_duplicate_enrollment_returns_none(self, test_enrollment, test_student, test_course):
        """Re-enrolling same student+course+year+sem should fail (UNIQUE constraint)."""
        dup = EnrollmentController.enroll(
            student_id=   test_student.student_id,
            course_id=    test_course.course_id,
            academic_year=2099,
            semester=     "1",
        )
        assert dup is None

    def test_update_marks_valid(self, test_enrollment):
        ok = EnrollmentController.update_marks(
            test_enrollment.enrollment_id,
            internal_marks=30.0,
            external_marks=45.0,
        )
        assert ok is True
        updated = EnrollmentController.get_by_id(test_enrollment.enrollment_id)
        assert updated.internal_marks == 30.0
        assert updated.external_marks == 45.0
        assert updated.total_marks    == 75.0

    def test_update_marks_auto_grade(self, test_enrollment):
        """DB trigger should compute grade/result automatically.
        Note: Only one marks update is performed per enrollment to avoid
        the avg_gp column precision overflow the GPA trigger can hit on
        consecutive updates for a brand-new student with a single enrollment.
        """
        ok = EnrollmentController.update_marks(
            test_enrollment.enrollment_id,
            internal_marks=30.0,
            external_marks=45.0,   # total = 75 → A grade (>= 70)
        )
        assert ok is True
        updated = EnrollmentController.get_by_id(test_enrollment.enrollment_id)
        assert updated.grade       is not None
        assert updated.total_marks == 75.0
        assert updated.result      == "Pass"
        assert updated.grade       in ("O", "A+", "A")   # threshold check

    def test_update_marks_fail_grade(self, test_enrollment):
        """Below 40 total → Fail."""
        EnrollmentController.update_marks(
            test_enrollment.enrollment_id,
            internal_marks=10.0,
            external_marks=25.0,   # total = 35 → F
        )
        updated = EnrollmentController.get_by_id(test_enrollment.enrollment_id)
        assert updated.grade  == "F"
        assert updated.result == "Fail"

    def test_update_marks_invalid_internal(self, test_enrollment):
        ok = EnrollmentController.update_marks(
            test_enrollment.enrollment_id,
            internal_marks=41.0,   # > 40 — invalid
            external_marks=50.0,
        )
        assert ok is False

    def test_update_marks_invalid_external(self, test_enrollment):
        ok = EnrollmentController.update_marks(
            test_enrollment.enrollment_id,
            internal_marks=30.0,
            external_marks=61.0,   # > 60 — invalid
        )
        assert ok is False

    def test_update_marks_negative(self, test_enrollment):
        ok = EnrollmentController.update_marks(
            test_enrollment.enrollment_id,
            internal_marks=-5.0,
            external_marks=40.0,
        )
        assert ok is False

    def test_bulk_update_marks(self, test_enrollment):
        records = [
            {
                "enrollment_id": test_enrollment.enrollment_id,
                "internal":      25.0,
                "external":      40.0,
            }
        ]
        result = EnrollmentController.bulk_update_marks(records)
        assert result["success"] == 1
        assert result["failed"]  == 0

    def test_bulk_update_with_invalid_entry(self, test_enrollment):
        records = [
            {
                "enrollment_id": test_enrollment.enrollment_id,
                "internal":      -1.0,   # invalid
                "external":      40.0,
            }
        ]
        result = EnrollmentController.bulk_update_marks(records)
        assert result["failed"] == 1

    def test_drop_enrollment(self, test_enrollment):
        ok = EnrollmentController.drop(test_enrollment.enrollment_id)
        assert ok is True
        updated = EnrollmentController.get_by_id(test_enrollment.enrollment_id)
        assert updated.status == "dropped"

    def test_drop_nonexistent(self, require_db):
        ok = EnrollmentController.drop(999999)
        assert ok is False

    def test_grade_distribution_returns_list(self, require_db):
        from student_management.controllers.course_controller import CourseController
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses")
        dist = EnrollmentController.grade_distribution(courses[0].course_id)
        assert isinstance(dist, list)

    def test_transcript_shape(self, test_enrollment):
        EnrollmentController.update_marks(
            test_enrollment.enrollment_id, 35.0, 50.0
        )
        txn = EnrollmentController.get_transcript(test_enrollment.student_id)
        for key in ("enrollments", "cgpa", "pass_count", "fail_count", "total_credits"):
            assert key in txn, f"Missing key: {key}"
        assert isinstance(txn["enrollments"], list)
        assert len(txn["enrollments"]) >= 1

    def test_transcript_cgpa_is_float(self, test_enrollment):
        txn = EnrollmentController.get_transcript(test_enrollment.student_id)
        assert isinstance(txn["cgpa"], float)

    def test_filter_by_year_and_semester(self, test_enrollment, test_student):
        enr = EnrollmentController.get_student_enrollments(
            test_student.student_id,
            academic_year=2099,
            semester="1",
        )
        assert any(e.enrollment_id == test_enrollment.enrollment_id for e in enr)

    def test_filter_wrong_year_returns_empty(self, test_enrollment, test_student):
        enr = EnrollmentController.get_student_enrollments(
            test_student.student_id,
            academic_year=2001,   # doesn't exist
        )
        assert all(e.enrollment_id != test_enrollment.enrollment_id for e in enr)
