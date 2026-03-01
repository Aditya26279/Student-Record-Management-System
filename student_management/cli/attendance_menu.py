"""
cli/attendance_menu.py — Attendance Management sub-menu
"""

from __future__ import annotations

from .base_menu import BaseMenu, MenuItem
from ..controllers.attendance_controller import AttendanceController
from ..controllers.course_controller     import CourseController
from ..controllers.student_controller    import StudentController
from ..utils.helpers import (print_table, print_header, print_success,
                              print_error, print_info, get_input,
                              confirm, today_str, format_attendance_pct)


class AttendanceMenu(BaseMenu):
    title = "Attendance Management"

    def __init__(self):
        super().__init__()
        self.items = [
            MenuItem("1", "Mark attendance (single student)", self._mark_single),
            MenuItem("2", "Bulk mark attendance (class)",     self._mark_bulk),
            MenuItem("3", "View attendance by date",          self._view_by_date),
            MenuItem("4", "View student attendance",          self._view_student),
            MenuItem("5", "Attendance summary (course)",      self._summary_course),
            MenuItem("6", "Attendance summary (student)",     self._summary_student),
            MenuItem("7", "View defaulters",                  self._defaulters),
            MenuItem("8", "List class dates",                 self._class_dates),
            MenuItem("0", "← Back to main menu",              self._go_back),
        ]

    # ── 1. Mark single ────────────────────────────────────────────────── #
    def _mark_single(self) -> None:
        print_header("Mark Attendance — Single Student")
        sid = self._get_student_id()
        if not sid: self._pause(); return
        cid = self._get_course_id()
        if not cid: self._pause(); return

        d      = get_input("Date (YYYY-MM-DD)", today_str())
        status = get_input("Status (Present/Absent/Late/OD)", "Present")

        ok = AttendanceController.mark(sid, cid, d, status)
        print_success("Attendance recorded.") if ok else print_error("Failed.")
        self._pause()

    # ── 2. Bulk mark (class) ──────────────────────────────────────────── #
    def _mark_bulk(self) -> None:
        print_header("Bulk Mark Attendance")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        c = CourseController.get_by_id(cid)
        if not c:
            print_error("Course not found."); self._pause(); return

        year_r = input("  Academic year: ").strip()
        year   = int(year_r) if year_r.isdigit() else None
        sem    = input("  Semester: ").strip() or None
        d      = get_input("Class date (YYYY-MM-DD)", today_str())

        from ..controllers.enrollment_controller import EnrollmentController
        enrollments = EnrollmentController.get_course_enrollments(cid, year)
        if sem:
            enrollments = [e for e in enrollments if e.semester == sem]

        if not enrollments:
            print_info("No enrolled students found."); self._pause(); return

        print_info(f"Marking attendance for {len(enrollments)} student(s) — {d}")
        print_info("Status: P=Present  A=Absent  L=Late  O=OD  (Enter=Absent)")
        records = []

        for e in enrollments:
            raw = input(f"    {e.student_code:15s} {e.student_name[:25]:<25}: ").strip().upper()
            status_map = {"P": "Present", "A": "Absent", "L": "Late", "O": "OD", "": "Absent"}
            status = status_map.get(raw, "Absent")
            records.append({"student_id": e.student_id, "status": status})

        if not confirm(f"Save attendance for {len(records)} students on {d}?"):
            print_info("Cancelled."); self._pause(); return

        result = AttendanceController.mark_bulk(cid, d, records)
        print_success(f"Done! Recorded: {result['success']}  Failed: {result['failed']}")
        self._pause()

    # ── 3. View by date ───────────────────────────────────────────────── #
    def _view_by_date(self) -> None:
        print_header("Attendance by Date")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        d = get_input("Date (YYYY-MM-DD)", today_str())
        records = AttendanceController.get_by_date(cid, d)

        if not records:
            print_info(f"No attendance records for {d}."); self._pause(); return

        rows = [
            {
                "Code":   r.student_code,
                "Name":   r.student_name,
                "Status": r.status,
                "Remarks":r.remarks or "—",
            }
            for r in records
        ]
        present = sum(1 for r in records if r.status == "Present")
        absent  = sum(1 for r in records if r.status == "Absent")
        print_table(rows, title=f"Attendance on {d}  |  Present: {present}  Absent: {absent}")
        self._pause()

    # ── 4. View student attendance ────────────────────────────────────── #
    def _view_student(self) -> None:
        print_header("Student Attendance Records")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        s = StudentController.get_by_id(sid)
        if not s:
            print_error("Student not found."); self._pause(); return

        cid_r = input("  Course ID (Enter for all): ").strip()
        cid   = int(cid_r) if cid_r.isdigit() else None
        from_d = input("  From date (YYYY-MM-DD, Enter to skip): ").strip() or None
        to_d   = input("  To date   (YYYY-MM-DD, Enter to skip): ").strip() or None

        records = AttendanceController.get_student_attendance(sid, cid, from_d, to_d)
        if not records:
            print_info("No records found."); self._pause(); return

        rows = [
            {
                "Date":    r.attend_date,
                "Course":  r.course_code,
                "Status":  r.status,
                "Remarks": r.remarks or "—",
            }
            for r in records
        ]
        print_table(rows, title=f"{s.full_name} — {len(records)} record(s)")
        self._pause()

    # ── 5. Summary (course) ───────────────────────────────────────────── #
    def _summary_course(self) -> None:
        print_header("Attendance Summary — Course")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        summaries = AttendanceController.get_summary(course_id=cid)
        if not summaries:
            print_info("No attendance data."); self._pause(); return

        rows = [
            {
                "Code":    s.student_code,
                "Name":    s.student_name,
                "Total":   s.total_classes,
                "Present": s.present_count,
                "Absent":  s.absent_count,
                "Late":    s.late_count,
                "Attend%": f"{s.attendance_pct:.1f}%",
                "Eligible":"\033[32mYes\033[0m" if s.is_eligible else "\033[31mNO\033[0m",
            }
            for s in summaries
        ]
        print_table(rows, title=f"Attendance Summary — Course {cid}")
        self._pause()

    # ── 6. Summary (student) ──────────────────────────────────────────── #
    def _summary_student(self) -> None:
        print_header("Attendance Summary — Student")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        summaries = AttendanceController.get_summary(student_id=sid)
        if not summaries:
            print_info("No attendance data."); self._pause(); return

        s = StudentController.get_by_id(sid)
        rows = [
            {
                "Course":   sm.course_code,
                "Name":     sm.course_name[:30],
                "Total":    sm.total_classes,
                "Present":  sm.present_count,
                "Absent":   sm.absent_count,
                "Attend%":  f"{sm.attendance_pct:.1f}%",
                "Eligible": "Yes" if sm.is_eligible else "NO ⚠",
            }
            for sm in summaries
        ]
        name = s.full_name if s else f"Student {sid}"
        print_table(rows, title=f"{name} — Attendance by Course")
        self._pause()

    # ── 7. Defaulters ─────────────────────────────────────────────────── #
    def _defaulters(self) -> None:
        print_header("Attendance Defaulters")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        thr_r = input("  Threshold % [75]: ").strip()
        thr   = float(thr_r) if thr_r.replace(".", "").isdigit() else 75.0

        defaulters = AttendanceController.get_defaulters(cid, thr)
        if not defaulters:
            print_success(f"No defaulters below {thr}%!"); self._pause(); return

        rows = [
            {
                "Code":     d.student_code,
                "Name":     d.student_name,
                "Total":    d.total_classes,
                "Present":  d.present_count,
                "Attend%":  f"{d.attendance_pct:.1f}%",
                "Shortage": f"{max(0, thr - d.attendance_pct):.1f}%",
            }
            for d in defaulters
        ]
        print_table(rows, title=f"{len(defaulters)} defaulter(s) below {thr}%")
        self._pause()

    # ── 8. Class dates ────────────────────────────────────────────────── #
    def _class_dates(self) -> None:
        print_header("Class Dates")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        dates = AttendanceController.get_course_attendance_dates(cid)
        if not dates:
            print_info("No attendance dates found."); self._pause(); return

        print_info(f"Total classes held: {len(dates)}")
        for i, d in enumerate(dates, 1):
            print(f"  {i:3}. {d}")
        print()
        self._pause()
