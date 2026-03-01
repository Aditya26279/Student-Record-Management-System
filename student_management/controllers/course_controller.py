"""
controllers/course_controller.py — CRUD for Courses
"""

from __future__ import annotations
from typing import List, Optional

from ..config.database import execute_query, execute_non_query, db_session
from ..models.course   import Course
from ..utils.logger    import setup_logger

log = setup_logger("course_ctrl")


class CourseController:

    # ── CREATE ─────────────────────────────────────────────────────────── #
    @staticmethod
    def add(course_code: str, course_name: str, credits: int,
            semester: str, department_id: Optional[int] = None,
            description: str = "", max_students: int = 60) -> Optional[Course]:
        if not course_code or not course_name:
            log.error("course_code and course_name are required")
            return None
        sql = """
            INSERT INTO courses
                (course_code, course_name, description, credits,
                 department_id, semester, max_students)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with db_session() as cur:
                cur.execute(sql, (course_code, course_name, description,
                                  credits, department_id, semester, max_students))
                new_id = cur.lastrowid
            log.info("Course added — ID %d  [%s]", new_id, course_code)
            return CourseController.get_by_id(new_id)
        except Exception as exc:
            log.error("add_course failed: %s", exc)
            return None

    # ── READ ───────────────────────────────────────────────────────────── #
    @staticmethod
    def get_by_id(course_id: int) -> Optional[Course]:
        rows = execute_query(
            "SELECT c.*, d.dept_name FROM courses c "
            "LEFT JOIN departments d ON c.department_id = d.department_id "
            "WHERE c.course_id = %s", (course_id,)
        )
        return Course.from_row(rows[0]) if rows else None

    @staticmethod
    def get_by_code(code: str) -> Optional[Course]:
        rows = execute_query(
            "SELECT c.*, d.dept_name FROM courses c "
            "LEFT JOIN departments d ON c.department_id = d.department_id "
            "WHERE c.course_code = %s", (code,)
        )
        return Course.from_row(rows[0]) if rows else None

    @staticmethod
    def get_all(department_id: Optional[int] = None,
                semester: Optional[str] = None,
                active_only: bool = True) -> List[Course]:
        sql = ("SELECT c.*, d.dept_name FROM courses c "
               "LEFT JOIN departments d ON c.department_id = d.department_id "
               "WHERE 1=1 ")
        params: list = []
        if active_only:
            sql += "AND c.is_active = TRUE "
        if department_id:
            sql += "AND c.department_id = %s "; params.append(department_id)
        if semester:
            sql += "AND c.semester = %s "; params.append(semester)
        sql += "ORDER BY c.semester, c.course_code"
        return [Course.from_row(r) for r in execute_query(sql, tuple(params))]

    @staticmethod
    def get_summary() -> List[Course]:
        """Return courses with enrollment statistics from the view."""
        rows = execute_query(
            "SELECT * FROM vw_course_enrollment_summary ORDER BY course_code"
        )
        return [Course.from_row(r) for r in rows]

    @staticmethod
    def search(keyword: str) -> List[Course]:
        like = f"%{keyword}%"
        sql  = ("SELECT c.*, d.dept_name FROM courses c "
                "LEFT JOIN departments d ON c.department_id = d.department_id "
                "WHERE c.course_code LIKE %s OR c.course_name LIKE %s "
                "ORDER BY c.course_code")
        return [Course.from_row(r) for r in execute_query(sql, (like, like))]

    # ── UPDATE ─────────────────────────────────────────────────────────── #
    @staticmethod
    def update(course_id: int, **kwargs) -> bool:
        allowed = {"course_name", "description", "credits", "max_students",
                   "semester", "department_id", "is_active"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = %s" for k in fields)
        params     = list(fields.values()) + [course_id]
        try:
            rows = execute_non_query(
                f"UPDATE courses SET {set_clause} WHERE course_id = %s",
                tuple(params)
            )
            return rows > 0
        except Exception as exc:
            log.error("update_course: %s", exc)
            return False

    @staticmethod
    def deactivate(course_id: int) -> bool:
        return CourseController.update(course_id, is_active=False)

    # ── STATS ──────────────────────────────────────────────────────────── #
    @staticmethod
    def get_enrolled_students(course_id: int,
                              academic_year: Optional[int] = None,
                              semester: Optional[str] = None) -> List[dict]:
        sql = """
            SELECT s.student_id, s.student_code,
                   CONCAT(s.first_name,' ',s.last_name) AS student_name,
                   s.email, e.grade, e.result, e.total_marks, e.status
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            WHERE e.course_id = %s
        """
        params: list = [course_id]
        if academic_year:
            sql += " AND e.academic_year = %s"; params.append(academic_year)
        if semester:
            sql += " AND e.semester = %s"; params.append(semester)
        sql += " ORDER BY s.last_name, s.first_name"
        return execute_query(sql, tuple(params))
