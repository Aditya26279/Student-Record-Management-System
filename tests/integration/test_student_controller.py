"""
tests/integration/test_student_controller.py
Integration tests for StudentController — requires live DB.
Each test uses the `test_student` fixture to create an isolated record
that is automatically cleaned up after the test.
"""

import pytest
from student_management.controllers.student_controller import StudentController


pytestmark = pytest.mark.integration


class TestStudentControllerRead:
    """Tests that only read existing seed data."""

    def test_get_all_returns_list(self, require_db):
        students = StudentController.get_all()
        assert isinstance(students, list)
        assert len(students) > 0

    def test_get_all_active_only(self, require_db):
        active = StudentController.get_all(status="active")
        assert all(s.status == "active" for s in active)

    def test_get_all_graduated(self, require_db):
        grads = StudentController.get_all(status="graduated")
        assert all(s.status == "graduated" for s in grads)

    def test_get_all_by_department(self, require_db, cs_dept_id):
        students = StudentController.get_all(department_id=cs_dept_id)
        assert all(s.department_id == cs_dept_id for s in students)

    def test_get_by_id_valid(self, require_db):
        students = StudentController.get_all()
        first    = students[0]
        fetched  = StudentController.get_by_id(first.student_id)
        assert fetched is not None
        assert fetched.student_id == first.student_id

    def test_get_by_id_nonexistent(self, require_db):
        s = StudentController.get_by_id(999999)
        assert s is None

    def test_get_by_code_valid(self, require_db):
        students = StudentController.get_all()
        first    = students[0]
        fetched  = StudentController.get_by_code(first.student_code)
        assert fetched is not None
        assert fetched.student_code == first.student_code

    def test_get_by_code_invalid(self, require_db):
        s = StudentController.get_by_code("XXXX_NOPE")
        assert s is None

    def test_search_returns_results(self, require_db):
        results = StudentController.search("a")    # common letter
        assert len(results) > 0

    def test_search_no_results(self, require_db):
        results = StudentController.search("ZZZZZZQQQQ")
        assert results == []

    def test_get_statistics_shape(self, require_db):
        stats = StudentController.get_statistics()
        for key in ("total", "active", "avg_gpa"):
            assert key in stats, f"Missing key: {key}"
        assert int(stats["total"]) > 0

    def test_get_topper_count(self, require_db):
        toppers = StudentController.get_topper(3)
        assert len(toppers) <= 3

    def test_get_topper_ordered_by_gpa(self, require_db):
        toppers = StudentController.get_topper(5)
        gpas    = [t.gpa for t in toppers]
        assert gpas == sorted(gpas, reverse=True)

    def test_get_departments(self, require_db):
        depts = StudentController.get_departments()
        assert len(depts) > 0
        assert "department_id" in depts[0]
        assert "dept_name"     in depts[0]


class TestStudentControllerWrite:
    """Tests that create/modify/delete — use `test_student` fixture for isolation."""

    def test_add_student_returns_object(self, test_student):
        assert test_student is not None
        assert test_student.student_id is not None
        assert test_student.student_code.startswith("STU")

    def test_added_student_readable(self, test_student):
        fetched = StudentController.get_by_id(test_student.student_id)
        assert fetched is not None
        assert fetched.first_name == "PytestFirst"

    def test_add_student_invalid_email(self, require_db, cs_dept_id):
        s = StudentController.add(
            first_name="Bad", last_name="Email",
            dob="2002-01-01", gender="Male",
            email="not-valid",   # invalid
            department_id=cs_dept_id,
        )
        assert s is None

    def test_add_student_invalid_dob(self, require_db, cs_dept_id):
        s = StudentController.add(
            first_name="Bad", last_name="DOB",
            dob="1800-01-01",    # unreasonable age
            gender="Female",
            email="valid@test.io",
        )
        assert s is None

    def test_update_student_phone(self, test_student):
        ok = StudentController.update(
            test_student.student_id, phone="8888888888"
        )
        assert ok is True
        updated = StudentController.get_by_id(test_student.student_id)
        assert updated.phone == "8888888888"

    def test_update_student_name(self, test_student):
        ok = StudentController.update(
            test_student.student_id,
            first_name="Updated",
            last_name= "Name",
        )
        assert ok is True
        updated = StudentController.get_by_id(test_student.student_id)
        assert updated.first_name == "Updated"
        assert updated.last_name  == "Name"

    def test_update_nonexistent_student(self, require_db):
        ok = StudentController.update(999999, phone="0000000000")
        assert ok is False

    def test_change_status_graduated(self, test_student):
        ok = StudentController.change_status(test_student.student_id, "graduated")
        assert ok is True
        updated = StudentController.get_by_id(test_student.student_id)
        assert updated.status == "graduated"

    def test_change_status_invalid(self, test_student):
        ok = StudentController.change_status(test_student.student_id, "alien")
        assert ok is False

    def test_soft_delete(self, test_student):
        ok = StudentController.delete(test_student.student_id)
        assert ok is True
        updated = StudentController.get_by_id(test_student.student_id)
        assert updated.status == "inactive"

    def test_search_finds_new_student(self, test_student):
        # Search by email fragment unique to test student
        results = StudentController.search("pytest_")
        assert any(s.student_id == test_student.student_id for s in results)
