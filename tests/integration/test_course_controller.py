"""
tests/integration/test_course_controller.py
Integration tests for CourseController — requires live DB.
"""

import pytest
from student_management.controllers.course_controller import CourseController


pytestmark = pytest.mark.integration


class TestCourseControllerRead:

    def test_get_all_returns_list(self, require_db):
        courses = CourseController.get_all()
        assert isinstance(courses, list)
        assert len(courses) > 0

    def test_get_all_active_by_default(self, require_db):
        courses = CourseController.get_all(active_only=True)
        assert all(c.is_active for c in courses)

    def test_get_all_by_semester(self, require_db):
        courses = CourseController.get_all(semester="1")
        assert all(c.semester == "1" for c in courses)

    def test_get_all_by_department(self, require_db, cs_dept_id):
        courses = CourseController.get_all(department_id=cs_dept_id)
        assert all(c.department_id == cs_dept_id for c in courses)

    def test_get_by_id_valid(self, require_db):
        courses = CourseController.get_all()
        first   = courses[0]
        fetched = CourseController.get_by_id(first.course_id)
        assert fetched is not None
        assert fetched.course_id == first.course_id

    def test_get_by_id_nonexistent(self, require_db):
        c = CourseController.get_by_id(999999)
        assert c is None

    def test_get_by_code_valid(self, require_db):
        courses = CourseController.get_all()
        first   = courses[0]
        fetched = CourseController.get_by_code(first.course_code)
        assert fetched is not None
        assert fetched.course_code == first.course_code

    def test_get_by_code_invalid(self, require_db):
        c = CourseController.get_by_code("XXXX999")
        assert c is None

    def test_search_returns_results(self, require_db):
        results = CourseController.search("cs")
        assert isinstance(results, list)

    def test_search_no_results(self, require_db):
        results = CourseController.search("ZZZZQQQQ_NOPE")
        assert results == []

    def test_get_summary_has_stats(self, require_db):
        summaries = CourseController.get_summary()
        assert isinstance(summaries, list)
        # Check some have enrollment data
        assert any(c.enrolled_count >= 0 for c in summaries)

    def test_get_enrolled_students(self, require_db):
        courses = CourseController.get_all()
        if not courses:
            pytest.skip("No courses in DB")
        rows = CourseController.get_enrolled_students(courses[0].course_id)
        assert isinstance(rows, list)

    def test_seats_available_non_negative(self, require_db):
        courses = CourseController.get_all()
        for c in courses:
            assert c.seats_available >= 0


class TestCourseControllerWrite:

    def test_add_course_returns_object(self, test_course):
        assert test_course is not None
        assert test_course.course_id is not None
        assert test_course.course_code.startswith("TST")

    def test_added_course_readable(self, test_course):
        fetched = CourseController.get_by_id(test_course.course_id)
        assert fetched is not None
        assert fetched.credits == 3

    def test_add_course_missing_name_fails(self, require_db, cs_dept_id):
        c = CourseController.add(
            course_code="", course_name="", credits=3,
            semester="1", department_id=cs_dept_id,
        )
        assert c is None

    def test_update_course_name(self, test_course):
        ok = CourseController.update(test_course.course_id,
                                      course_name="Updated Course Name")
        assert ok is True
        updated = CourseController.get_by_id(test_course.course_id)
        assert updated.course_name == "Updated Course Name"

    def test_update_max_students(self, test_course):
        ok = CourseController.update(test_course.course_id, max_students=50)
        assert ok is True
        updated = CourseController.get_by_id(test_course.course_id)
        assert updated.max_students == 50

    def test_update_nonexistent_course(self, require_db):
        ok = CourseController.update(999999, course_name="Ghost")
        assert ok is False

    def test_deactivate_course(self, test_course):
        ok = CourseController.deactivate(test_course.course_id)
        assert ok is True
        updated = CourseController.get_by_id(test_course.course_id)
        assert updated.is_active is False

    def test_search_finds_added_course(self, test_course):
        keyword = test_course.course_code
        results = CourseController.search(keyword)
        assert any(c.course_id == test_course.course_id for c in results)
