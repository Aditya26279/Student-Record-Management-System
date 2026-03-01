"""
cli/enrollment_menu.py — Enrollment & Marks Management sub-menu
"""

from __future__ import annotations

from .base_menu import BaseMenu, MenuItem
from ..controllers.enrollment_controller import EnrollmentController
from ..controllers.student_controller    import StudentController
from ..controllers.course_controller     import CourseController
from ..utils.helpers import (print_table, print_header, print_success,
                              print_error, print_info, get_input,
                              confirm, current_year)


class EnrollmentMenu(BaseMenu):
    title = "Enrollment & Marks Management"

    def __init__(self):
        super().__init__()
        self.items = [
            MenuItem("1", "Enroll student in course",        self._enroll),
            MenuItem("2", "View student enrollments",        self._view_student),
            MenuItem("3", "View course enrollments",         self._view_course),
            MenuItem("4", "Update marks (single)",           self._update_marks),
            MenuItem("5", "Bulk marks entry (one course)",   self._bulk_marks),
            MenuItem("6", "Drop enrollment",                 self._drop),
            MenuItem("7", "View grade distribution",         self._grade_dist),
            MenuItem("8", "View student transcript",         self._transcript),
            MenuItem("0", "← Back to main menu",             self._go_back),
        ]

    # ── 1. Enroll ─────────────────────────────────────────────────────── #
    def _enroll(self) -> None:
        print_header("Enroll Student in Course")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        s = StudentController.get_by_id(sid)
        if not s:
            print_error(f"Student ID {sid} not found."); self._pause(); return
        print_info(f"Student : {s.full_name} [{s.student_code}]")

        cid = self._get_course_id()
        if not cid: self._pause(); return

        c = CourseController.get_by_id(cid)
        if not c:
            print_error(f"Course ID {cid} not found."); self._pause(); return
        print_info(f"Course  : [{c.course_code}] {c.course_name}  (Sem {c.semester})")
        print_info(f"Seats   : {c.enrolled_count}/{c.max_students}")

        year_r = input(f"  Academic Year [{current_year()}]: ").strip()
        year   = int(year_r) if year_r.isdigit() else current_year()
        sem    = get_input("Semester (1-8)", c.semester)
        fac_r  = input("  Faculty ID (optional): ").strip()
        fac_id = int(fac_r) if fac_r.isdigit() else None

        if not confirm(f"Enroll {s.full_name} in [{c.course_code}] for {year}/Sem{sem}?"):
            print_info("Cancelled."); self._pause(); return

        enroll = EnrollmentController.enroll(sid, cid, year, sem, fac_id)
        if enroll:
            print_success(f"Enrolled! Enrollment ID: {enroll.enrollment_id}")
        else:
            print_error("Enrollment failed. Student may already be enrolled.")
        self._pause()

    # ── 2. View student enrollments ───────────────────────────────────── #
    def _view_student(self) -> None:
        print_header("Student Enrollments")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        s = StudentController.get_by_id(sid)
        if not s:
            print_error("Student not found."); self._pause(); return

        year_r = input("  Academic year (Enter for all): ").strip()
        year   = int(year_r) if year_r.isdigit() else None
        sem    = input("  Semester (Enter for all): ").strip() or None

        enrollments = EnrollmentController.get_student_enrollments(sid, year, sem)
        if not enrollments:
            print_info("No enrollments found."); self._pause(); return

        rows = [
            {
                "Enroll ID":e.enrollment_id,
                "Course":   e.course_code,
                "Name":     e.course_name[:30],
                "Year":     e.academic_year,
                "Sem":      e.semester,
                "Int":      f"{e.internal_marks:.1f}" if e.internal_marks is not None else "—",
                "Ext":      f"{e.external_marks:.1f}" if e.external_marks is not None else "—",
                "Total":    f"{e.total_marks:.1f}"    if e.total_marks    is not None else "—",
                "Grade":    e.grade or "—",
                "Result":   e.result or "Incomplete",
            }
            for e in enrollments
        ]
        print_table(rows, title=f"{s.full_name} — {len(enrollments)} enrollment(s)")
        self._pause()

    # ── 3. View course enrollments ────────────────────────────────────── #
    def _view_course(self) -> None:
        print_header("Course Enrollments")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        year_r = input("  Academic year (Enter for all): ").strip()
        year   = int(year_r) if year_r.isdigit() else None

        enrollments = EnrollmentController.get_course_enrollments(cid, year)
        if not enrollments:
            print_info("No enrollments found."); self._pause(); return

        rows = [
            {
                "Enroll ID": e.enrollment_id,
                "Std Code":  e.student_code,
                "Name":      e.student_name,
                "Sem":       e.semester,
                "Year":      e.academic_year,
                "Total":     f"{e.total_marks:.1f}" if e.total_marks is not None else "—",
                "Grade":     e.grade or "—",
                "Result":    e.result or "Incomplete",
            }
            for e in enrollments
        ]
        print_table(rows, title=f"Course {cid} — {len(enrollments)} student(s)")
        self._pause()

    # ── 4. Update marks (single) ──────────────────────────────────────── #
    def _update_marks(self) -> None:
        print_header("Update Marks")
        eid_r = input("  Enrollment ID: ").strip()
        if not eid_r.isdigit():
            print_error("Invalid Enrollment ID."); self._pause(); return
        eid = int(eid_r)

        e = EnrollmentController.get_by_id(eid)
        if not e:
            print_error(f"Enrollment ID {eid} not found."); self._pause(); return

        print_info(f"Student : {e.student_name} [{e.student_code}]")
        print_info(f"Course  : [{e.course_code}] {e.course_name}")

        int_r = input("  Internal marks (0–40): ").strip()
        ext_r = input("  External marks (0–60): ").strip()

        try:
            internal = float(int_r)
            external = float(ext_r)
        except ValueError:
            print_error("Marks must be numeric."); self._pause(); return

        if not confirm(f"Set marks → Internal: {internal}, External: {external}?"):
            print_info("Cancelled."); self._pause(); return

        ok = EnrollmentController.update_marks(eid, internal, external)
        if ok:
            updated = EnrollmentController.get_by_id(eid)
            print_success(
                f"Marks updated! Total: {updated.total_marks}  "
                f"Grade: {updated.grade}  Result: {updated.result}"
            )
        else:
            print_error("Marks update failed.")
        self._pause()

    # ── 5. Bulk marks entry ───────────────────────────────────────────── #
    def _bulk_marks(self) -> None:
        print_header("Bulk Marks Entry")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        year_r = input(f"  Academic year [{current_year()}]: ").strip()
        year   = int(year_r) if year_r.isdigit() else current_year()
        sem    = input("  Semester: ").strip()

        enrollments = EnrollmentController.get_course_enrollments(cid, year)
        enrollments = [e for e in enrollments if e.semester == sem]

        if not enrollments:
            print_info("No students enrolled for this course/semester."); self._pause(); return

        print_info(f"Entering marks for {len(enrollments)} students")
        print_info("(Press Enter to skip a student)")
        records = []

        for e in enrollments:
            print(f"\n  \033[1;36m{e.student_code}  {e.student_name}\033[0m")
            int_r = input("    Internal (0-40): ").strip()
            ext_r = input("    External (0-60): ").strip()
            if int_r and ext_r:
                try:
                    records.append({
                        "enrollment_id": e.enrollment_id,
                        "internal":      float(int_r),
                        "external":      float(ext_r),
                    })
                except ValueError:
                    print_error("  Invalid — skipped")

        if not records:
            print_info("No records to save."); self._pause(); return

        if not confirm(f"Save marks for {len(records)} student(s)?"):
            print_info("Cancelled."); self._pause(); return

        result = EnrollmentController.bulk_update_marks(records)
        print_success(f"Done! Success: {result['success']}  Failed: {result['failed']}")
        self._pause()

    # ── 6. Drop enrollment ─────────────────────────────────────────────── #
    def _drop(self) -> None:
        print_header("Drop Enrollment")
        eid_r = input("  Enrollment ID: ").strip()
        if not eid_r.isdigit():
            print_error("Invalid ID."); self._pause(); return
        eid = int(eid_r)

        e = EnrollmentController.get_by_id(eid)
        if not e:
            print_error("Enrollment not found."); self._pause(); return

        print_info(f"{e.student_name} ← [{e.course_code}]  Year {e.academic_year}/Sem{e.semester}")

        if not confirm("Drop this enrollment?"):
            print_info("Cancelled."); self._pause(); return

        ok = EnrollmentController.drop(eid)
        print_success("Enrollment dropped.") if ok else print_error("Failed.")
        self._pause()

    # ── 7. Grade distribution ─────────────────────────────────────────── #
    def _grade_dist(self) -> None:
        print_header("Grade Distribution")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        year_r = input("  Academic year (Enter for all): ").strip()
        year   = int(year_r) if year_r.isdigit() else None

        dist = EnrollmentController.grade_distribution(cid, year)
        if not dist:
            print_info("No grade data available."); self._pause(); return

        print_table(dist, title=f"Grade Distribution — Course {cid}")

        # ASCII bar chart
        print("  Grade Chart:")
        for row in dist:
            grade = row.get("grade", "?")
            count = int(row.get("count", 0))
            pct   = float(row.get("percentage", 0))
            bar   = "█" * int(pct / 2)
            print(f"    {grade:>3}  {bar:<50}  {count:3d} ({pct:.1f}%)")
        print()
        self._pause()

    # ── 8. Transcript ─────────────────────────────────────────────────── #
    def _transcript(self) -> None:
        print_header("Student Transcript")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        txn = EnrollmentController.get_transcript(sid)
        if not txn.get("enrollments"):
            print_info("No enrollment records found."); self._pause(); return

        s = StudentController.get_by_id(sid)
        if s:
            print(f"\n  Student : {s.full_name} [{s.student_code}]")
            print(f"  Dept    : {s.department_name or '—'}")

        print(f"\n  CGPA          : \033[1;33m{txn['cgpa']:.2f}\033[0m")
        print(f"  Total Credits : {txn['total_credits']}")
        print(f"  Passed        : {txn['pass_count']}   Failed: {txn['fail_count']}")

        rows = [
            {
                "Course":   e.get("course_code", ""),
                "Name":     str(e.get("course_name", ""))[:28],
                "Sem":      e.get("semester", ""),
                "Year":     e.get("academic_year", ""),
                "Int":      e.get("internal_marks") or "—",
                "Ext":      e.get("external_marks") or "—",
                "Total":    e.get("total_marks") or "—",
                "Grade":    e.get("grade") or "—",
                "Result":   e.get("result") or "Incomplete",
            }
            for e in txn["enrollments"]
        ]
        print_table(rows, title="Courses")
        self._pause()
