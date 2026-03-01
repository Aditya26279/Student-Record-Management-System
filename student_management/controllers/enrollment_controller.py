"""
controllers/enrollment_controller.py — Enrollment & Marks management
"""

from __future__ import annotations
from typing import List, Optional

from ..config.database   import execute_query, execute_non_query, db_session
from ..models.enrollment import Enrollment
from ..utils.logger      import setup_logger
from ..utils.validators  import validate_marks

log = setup_logger("enrollment_ctrl")


class EnrollmentController:

    # ── ENROLL ─────────────────────────────────────────────────────────── #
    @staticmethod
    def enroll(student_id: int, course_id: int, academic_year: int,
               semester: str, faculty_id: Optional[int] = None) -> Optional[Enrollment]:
        """Enroll a student in a course (duplicate guard in DB via UNIQUE key)."""
        sql = """
            INSERT INTO enrollments
                (student_id, course_id, faculty_id, academic_year, semester)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with db_session() as cur:
                cur.execute(sql, (student_id, course_id, faculty_id,
                                  academic_year, semester))
                new_id = cur.lastrowid
            log.info("Student %d enrolled in course %d [sem %s/%d]",
                     student_id, course_id, semester, academic_year)
            return EnrollmentController.get_by_id(new_id)
        except Exception as exc:
            log.error("enroll failed: %s", exc)
            return None

    # ── READ ───────────────────────────────────────────────────────────── #
    @staticmethod
    def get_by_id(enrollment_id: int) -> Optional[Enrollment]:
        rows = execute_query(
            """SELECT e.*,
                      CONCAT(s.first_name,' ',s.last_name) AS student_name,
                      s.student_code,
                      c.course_code, c.course_name
               FROM enrollments e
               JOIN students s ON e.student_id = s.student_id
               JOIN courses  c ON e.course_id  = c.course_id
               WHERE e.enrollment_id = %s""",
            (enrollment_id,)
        )
        return Enrollment.from_row(rows[0]) if rows else None

    @staticmethod
    def get_student_enrollments(student_id: int,
                                academic_year: Optional[int] = None,
                                semester: Optional[str] = None) -> List[Enrollment]:
        sql = """
            SELECT e.*,
                   CONCAT(s.first_name,' ',s.last_name) AS student_name,
                   s.student_code,
                   c.course_code, c.course_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses  c ON e.course_id  = c.course_id
            WHERE e.student_id = %s
        """
        params: list = [student_id]
        if academic_year:
            sql += " AND e.academic_year = %s"; params.append(academic_year)
        if semester:
            sql += " AND e.semester = %s"; params.append(semester)
        sql += " ORDER BY e.academic_year, e.semester, c.course_code"
        return [Enrollment.from_row(r) for r in execute_query(sql, tuple(params))]

    @staticmethod
    def get_course_enrollments(course_id: int,
                               academic_year: Optional[int] = None) -> List[Enrollment]:
        sql = """
            SELECT e.*,
                   CONCAT(s.first_name,' ',s.last_name) AS student_name,
                   s.student_code,
                   c.course_code, c.course_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses  c ON e.course_id  = c.course_id
            WHERE e.course_id = %s
        """
        params: list = [course_id]
        if academic_year:
            sql += " AND e.academic_year = %s"; params.append(academic_year)
        sql += " ORDER BY s.last_name, s.first_name"
        return [Enrollment.from_row(r) for r in execute_query(sql, tuple(params))]

    # ── MARKS & GRADE ──────────────────────────────────────────────────── #
    @staticmethod
    def update_marks(enrollment_id: int,
                     internal_marks: float,
                     external_marks: float) -> bool:
        ok, msg = validate_marks(internal_marks, external_marks)
        if not ok:
            log.error("Marks validation: %s", msg)
            return False
        try:
            rows = execute_non_query(
                """UPDATE enrollments
                   SET internal_marks = %s,
                       external_marks = %s,
                       status = 'completed'
                   WHERE enrollment_id = %s""",
                (internal_marks, external_marks, enrollment_id)
            )
            if rows:
                log.info("Marks updated for enrollment %d", enrollment_id)
            return rows > 0
        except Exception as exc:
            log.error("update_marks: %s", exc)
            return False

    @staticmethod
    def bulk_update_marks(records: List[dict]) -> dict:
        """
        records = [{"enrollment_id": int, "internal": float, "external": float}, ...]
        Returns {"success": n, "failed": n}
        """
        success = failed = 0
        for rec in records:
            ok = EnrollmentController.update_marks(
                rec["enrollment_id"], rec["internal"], rec["external"]
            )
            if ok: success += 1
            else:  failed  += 1
        return {"success": success, "failed": failed}

    # ── DROP ───────────────────────────────────────────────────────────── #
    @staticmethod
    def drop(enrollment_id: int) -> bool:
        rows = execute_non_query(
            "UPDATE enrollments SET status = 'dropped' WHERE enrollment_id = %s",
            (enrollment_id,)
        )
        return rows > 0

    # ── GRADE DISTRIBUTION ─────────────────────────────────────────────── #
    @staticmethod
    def grade_distribution(course_id: int,
                           academic_year: Optional[int] = None) -> List[dict]:
        sql = """
            SELECT grade,
                   MIN(grade_points) AS grade_points,
                   COUNT(*) AS count,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM enrollments
            WHERE course_id = %s AND grade IS NOT NULL
        """
        params: list = [course_id]
        if academic_year:
            sql += " AND academic_year = %s"; params.append(academic_year)
        sql += " GROUP BY grade ORDER BY MIN(grade_points) DESC"
        return execute_query(sql, tuple(params))

    # ── TRANSCRIPT ─────────────────────────────────────────────────────── #
    @staticmethod
    def get_transcript(student_id: int) -> dict:
        """Return full academic transcript for a student."""
        enrollments = EnrollmentController.get_student_enrollments(student_id)
        completed   = [e for e in enrollments if e.status == "completed"]

        total_credits = 0
        earned_points = 0.0
        for e in completed:
            from ..models.course import Course
            course = execute_query(
                "SELECT credits FROM courses WHERE course_id = %s", (e.course_id,)
            )
            credits = int(course[0]["credits"]) if course else 0
            if e.grade_points is not None:
                total_credits += credits
                earned_points += credits * e.grade_points

        cgpa = round(earned_points / total_credits, 2) if total_credits else 0.0
        return {
            "enrollments":    [e.to_dict() for e in enrollments],
            "total_credits":  total_credits,
            "earned_points":  round(earned_points, 2),
            "cgpa":           cgpa,
            "pass_count":     sum(1 for e in completed if e.is_passed),
            "fail_count":     sum(1 for e in completed if not e.is_passed),
        }
