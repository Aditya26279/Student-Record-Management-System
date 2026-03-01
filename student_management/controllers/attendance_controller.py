"""
controllers/attendance_controller.py — Attendance marking and querying
"""

from __future__ import annotations
from typing import List, Optional

from ..config.database   import execute_query, execute_non_query, db_session
from ..models.attendance import Attendance, AttendanceSummary
from ..utils.logger      import setup_logger
from ..utils.validators  import validate_attendance_status, validate_date

log = setup_logger("attendance_ctrl")


class AttendanceController:

    # ── MARK ───────────────────────────────────────────────────────────── #
    @staticmethod
    def mark(student_id: int, course_id: int, date: str,
             status: str, marked_by: Optional[int] = None,
             remarks: str = "") -> bool:
        """Upsert attendance for one student on one date."""
        ok, msg = validate_attendance_status(status)
        if not ok:
            log.error("Invalid status: %s", msg)
            return False
        ok, msg = validate_date(date)
        if not ok:
            log.error("Invalid date: %s", msg)
            return False

        sql = """
            INSERT INTO attendance (student_id, course_id, attend_date,
                                    status, marked_by, remarks)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status     = VALUES(status),
                marked_by  = VALUES(marked_by),
                remarks    = VALUES(remarks)
        """
        try:
            execute_non_query(sql, (student_id, course_id, date,
                                    status, marked_by, remarks))
            return True
        except Exception as exc:
            log.error("mark_attendance: %s", exc)
            return False

    @staticmethod
    def mark_bulk(course_id: int, date: str,
                  records: List[dict],
                  marked_by: Optional[int] = None) -> dict:
        """
        records = [{"student_id": int, "status": str, "remarks": str}, ...]
        Returns {"success": n, "failed": n}
        """
        ok, msg = validate_date(date)
        if not ok:
            log.error("Bulk mark: %s", msg)
            return {"success": 0, "failed": len(records)}

        success = failed = 0
        for rec in records:
            result = AttendanceController.mark(
                rec["student_id"], course_id, date,
                rec.get("status", "Absent"),
                marked_by,
                rec.get("remarks", "")
            )
            if result: success += 1
            else:      failed  += 1
        log.info("Bulk attendance: %d success / %d failed", success, failed)
        return {"success": success, "failed": failed}

    # ── READ ───────────────────────────────────────────────────────────── #
    @staticmethod
    def get_by_date(course_id: int, date: str) -> List[Attendance]:
        rows = execute_query(
            """SELECT a.*,
                      CONCAT(s.first_name,' ',s.last_name) AS student_name,
                      s.student_code, c.course_code, c.course_name
               FROM attendance a
               JOIN students s ON a.student_id = s.student_id
               JOIN courses  c ON a.course_id  = c.course_id
               WHERE a.course_id = %s AND a.attend_date = %s
               ORDER BY s.last_name, s.first_name""",
            (course_id, date)
        )
        return [Attendance.from_row(r) for r in rows]

    @staticmethod
    def get_student_attendance(student_id: int,
                               course_id: Optional[int] = None,
                               from_date: Optional[str] = None,
                               to_date: Optional[str] = None) -> List[Attendance]:
        sql = """
            SELECT a.*,
                   CONCAT(s.first_name,' ',s.last_name) AS student_name,
                   s.student_code, c.course_code, c.course_name
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses  c ON a.course_id  = c.course_id
            WHERE a.student_id = %s
        """
        params: list = [student_id]
        if course_id:
            sql += " AND a.course_id = %s"; params.append(course_id)
        if from_date:
            sql += " AND a.attend_date >= %s"; params.append(from_date)
        if to_date:
            sql += " AND a.attend_date <= %s"; params.append(to_date)
        sql += " ORDER BY a.attend_date DESC, c.course_code"
        return [Attendance.from_row(r) for r in execute_query(sql, tuple(params))]

    # ── SUMMARY / STATS ────────────────────────────────────────────────── #
    @staticmethod
    def get_summary(student_id: Optional[int] = None,
                    course_id: Optional[int] = None) -> List[AttendanceSummary]:
        sql = "SELECT * FROM vw_attendance_summary WHERE 1=1 "
        params: list = []
        if student_id:
            sql += "AND student_id = %s "; params.append(student_id)
        if course_id:
            sql += "AND course_id = %s "; params.append(course_id)
        sql += "ORDER BY student_name, course_code"
        return [AttendanceSummary.from_row(r) for r in execute_query(sql, tuple(params))]

    @staticmethod
    def get_defaulters(course_id: int,
                       threshold_pct: float = 75.0) -> List[AttendanceSummary]:
        """Return students below the attendance threshold for a course."""
        all_summaries = AttendanceController.get_summary(course_id=course_id)
        return [s for s in all_summaries if s.attendance_pct < threshold_pct]

    @staticmethod
    def get_course_attendance_dates(course_id: int) -> List[str]:
        rows = execute_query(
            "SELECT DISTINCT attend_date FROM attendance "
            "WHERE course_id = %s ORDER BY attend_date",
            (course_id,)
        )
        return [str(r["attend_date"]) for r in rows]
