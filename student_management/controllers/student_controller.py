"""
controllers/student_controller.py — Full CRUD for Students
"""

from __future__ import annotations
from typing import List, Optional

from ..config.database import db_session, execute_query, execute_non_query
from ..models.student  import Student
from ..utils.logger    import setup_logger
from ..utils.validators import validate_student

log = setup_logger("student_ctrl")


class StudentController:
    """All student-related database operations."""

    # ── CREATE ─────────────────────────────────────────────────────────── #
    @staticmethod
    def add(first_name: str, last_name: str, dob: str, gender: str,
            email: str, phone: str = "", address: str = "",
            department_id: Optional[int] = None) -> Optional[Student]:
        """Insert a new student and return the created Student object."""
        data = dict(first_name=first_name, last_name=last_name,
                    date_of_birth=dob, gender=gender, email=email,
                    phone=phone)
        ok, msg = validate_student(data)
        if not ok:
            log.error("Validation failed: %s", msg)
            return None

        sql = """
            INSERT INTO students
                (first_name, last_name, date_of_birth, gender,
                 email, phone, address, department_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with db_session() as cur:
                cur.execute(sql, (first_name, last_name, dob, gender,
                                  email, phone, address, department_id))
                new_id = cur.lastrowid
            log.info("Student added — ID %d", new_id)
            return StudentController.get_by_id(new_id)
        except Exception as exc:
            log.error("add_student failed: %s", exc)
            return None

    # ── READ ───────────────────────────────────────────────────────────── #
    @staticmethod
    def get_by_id(student_id: int) -> Optional[Student]:
        rows = execute_query(
            "SELECT s.*, d.dept_name FROM students s "
            "LEFT JOIN departments d ON s.department_id = d.department_id "
            "WHERE s.student_id = %s", (student_id,)
        )
        return Student.from_row(rows[0]) if rows else None

    @staticmethod
    def get_by_code(code: str) -> Optional[Student]:
        rows = execute_query(
            "SELECT s.*, d.dept_name FROM students s "
            "LEFT JOIN departments d ON s.department_id = d.department_id "
            "WHERE s.student_code = %s", (code,)
        )
        return Student.from_row(rows[0]) if rows else None

    @staticmethod
    def get_all(status: Optional[str] = None,
                department_id: Optional[int] = None) -> List[Student]:
        sql = ("SELECT s.*, d.dept_name FROM students s "
               "LEFT JOIN departments d ON s.department_id = d.department_id "
               "WHERE 1=1 ")
        params: list = []
        if status:
            sql += "AND s.status = %s "; params.append(status)
        if department_id:
            sql += "AND s.department_id = %s "; params.append(department_id)
        sql += "ORDER BY s.last_name, s.first_name"
        return [Student.from_row(r) for r in execute_query(sql, tuple(params))]

    @staticmethod
    def search(keyword: str) -> List[Student]:
        """Full-text search across name, email, and student_code."""
        like = f"%{keyword}%"
        sql = """
            SELECT s.*, d.dept_name FROM students s
            LEFT JOIN departments d ON s.department_id = d.department_id
            WHERE s.first_name   LIKE %s
               OR s.last_name    LIKE %s
               OR s.email        LIKE %s
               OR s.student_code LIKE %s
            ORDER BY s.last_name, s.first_name
        """
        return [Student.from_row(r)
                for r in execute_query(sql, (like, like, like, like))]

    # ── UPDATE ─────────────────────────────────────────────────────────── #
    @staticmethod
    def update(student_id: int, **kwargs) -> bool:
        """Update any subset of student fields."""
        allowed = {"first_name", "last_name", "phone", "address",
                   "status", "department_id", "gender"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not fields:
            log.warning("update_student: no valid fields provided")
            return False
        set_clause = ", ".join(f"{k} = %s" for k in fields)
        params     = list(fields.values()) + [student_id]
        try:
            rows = execute_non_query(
                f"UPDATE students SET {set_clause} WHERE student_id = %s",
                tuple(params)
            )
            ok = rows > 0
            if ok:
                log.info("Student %d updated: %s", student_id, list(fields))
            return ok
        except Exception as exc:
            log.error("update_student failed: %s", exc)
            return False

    @staticmethod
    def change_status(student_id: int,
                      status: str) -> bool:
        """Quick helper to change enrolment status."""
        valid = ("active", "inactive", "graduated", "suspended")
        if status not in valid:
            log.error("Invalid status '%s'", status)
            return False
        return StudentController.update(student_id, status=status)

    # ── DELETE (soft) ──────────────────────────────────────────────────── #
    @staticmethod
    def delete(student_id: int) -> bool:
        """Soft-delete: sets status = 'inactive'."""
        return StudentController.change_status(student_id, "inactive")

    # ── STATS ──────────────────────────────────────────────────────────── #
    @staticmethod
    def get_statistics() -> dict:
        sql = """
            SELECT
                COUNT(*)                                             AS total,
                SUM(status = 'active')                              AS active,
                SUM(status = 'graduated')                           AS graduated,
                SUM(status = 'inactive' OR status = 'suspended')    AS inactive,
                ROUND(AVG(gpa), 2)                                  AS avg_gpa,
                MAX(gpa)                                            AS max_gpa,
                MIN(CASE WHEN gpa > 0 THEN gpa END)                 AS min_gpa
            FROM students
        """
        rows = execute_query(sql)
        return dict(rows[0]) if rows else {}

    @staticmethod
    def get_topper(limit: int = 5) -> List[Student]:
        sql = ("SELECT s.*, d.dept_name FROM students s "
               "LEFT JOIN departments d ON s.department_id = d.department_id "
               "WHERE s.status = 'active' "
               "ORDER BY s.gpa DESC LIMIT %s")
        return [Student.from_row(r) for r in execute_query(sql, (limit,))]

    @staticmethod
    def get_departments() -> List[dict]:
        return execute_query(
            "SELECT department_id, dept_code, dept_name FROM departments ORDER BY dept_name"
        )
