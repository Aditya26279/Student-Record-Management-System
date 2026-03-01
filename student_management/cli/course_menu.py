"""
cli/course_menu.py — Course Management sub-menu
"""

from __future__ import annotations

from .base_menu import BaseMenu, MenuItem
from ..controllers.course_controller import CourseController
from ..utils.helpers import (print_table, print_header, print_success,
                              print_error, print_info, get_input, confirm)


class CourseMenu(BaseMenu):
    title = "Course Management"

    def __init__(self):
        super().__init__()
        self.items = [
            MenuItem("1", "List all courses",              self._list_all),
            MenuItem("2", "Search courses",                self._search),
            MenuItem("3", "View course details",           self._view_detail),
            MenuItem("4", "View enrolled students",        self._enrolled_students),
            MenuItem("5", "Course enrollment summary",     self._summary),
            MenuItem("6", "Add new course",                self._add),
            MenuItem("7", "Update course",                 self._update),
            MenuItem("8", "Deactivate course",             self._deactivate),
            MenuItem("0", "← Back to main menu",           self._go_back),
        ]

    # ── 1. List all ───────────────────────────────────────────────────── #
    def _list_all(self) -> None:
        print_header("All Courses")
        sem_filter = input("  Semester filter (1-8 or Enter for all): ").strip() or None
        courses = CourseController.get_all(semester=sem_filter)
        if not courses:
            print_info("No courses found."); self._pause(); return

        rows = [
            {
                "ID":      c.course_id,
                "Code":    c.course_code,
                "Name":    c.course_name[:35],
                "Sem":     c.semester,
                "Credits": c.credits,
                "Dept":    c.department_name or "—",
                "Active":  "Yes" if c.is_active else "No",
            }
            for c in courses
        ]
        print_table(rows, title=f"{len(courses)} course(s)")
        self._pause()

    # ── 2. Search ─────────────────────────────────────────────────────── #
    def _search(self) -> None:
        print_header("Search Courses")
        keyword = get_input("Course code or name keyword")
        if not keyword:
            print_error("Keyword required."); self._pause(); return

        results = CourseController.search(keyword)
        if not results:
            print_info(f"No courses matching '{keyword}'."); self._pause(); return

        rows = [
            {
                "ID":      c.course_id,
                "Code":    c.course_code,
                "Name":    c.course_name[:35],
                "Sem":     c.semester,
                "Credits": c.credits,
            }
            for c in results
        ]
        print_table(rows, title=f"{len(results)} result(s)")
        self._pause()

    # ── 3. View detail ────────────────────────────────────────────────── #
    def _view_detail(self) -> None:
        print_header("Course Details")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        c = CourseController.get_by_id(cid)
        if not c:
            print_error(f"Course ID {cid} not found."); self._pause(); return

        print()
        print(f"  {'ID':<20}: {c.course_id}")
        print(f"  {'Course Code':<20}: {c.course_code}")
        print(f"  {'Course Name':<20}: {c.course_name}")
        print(f"  {'Description':<20}: {c.description or '—'}")
        print(f"  {'Credits':<20}: {c.credits}")
        print(f"  {'Semester':<20}: {c.semester}")
        print(f"  {'Department':<20}: {c.department_name or '—'}")
        print(f"  {'Max Students':<20}: {c.max_students}")
        print(f"  {'Active':<20}: {'Yes' if c.is_active else 'No'}")
        self._pause()

    # ── 4. Enrolled students ──────────────────────────────────────────── #
    def _enrolled_students(self) -> None:
        print_header("Enrolled Students")
        cid  = self._get_course_id()
        if not cid: self._pause(); return

        year_raw = input("  Academic year (e.g. 2024 or Enter for all): ").strip()
        year     = int(year_raw) if year_raw.isdigit() else None

        rows = CourseController.get_enrolled_students(cid, academic_year=year)
        if not rows:
            print_info("No students enrolled."); self._pause(); return

        display = [
            {
                "Code":    r["student_code"],
                "Name":    r["student_name"],
                "Total":   r.get("total_marks") or "—",
                "Grade":   r.get("grade") or "—",
                "Result":  r.get("result") or "Incomplete",
                "Status":  r.get("status", ""),
            }
            for r in rows
        ]
        print_table(display, title=f"{len(rows)} enrolled student(s)")
        self._pause()

    # ── 5. Enrollment summary ─────────────────────────────────────────── #
    def _summary(self) -> None:
        print_header("Course Enrollment Summary")
        courses = CourseController.get_summary()
        rows = [
            {
                "Code":      c.course_code,
                "Name":      c.course_name[:30],
                "Enrolled":  c.enrolled_count,
                "Max":       c.max_students,
                "Available": c.seats_available,
                "Avg Marks": f"{c.avg_marks:.1f}" if c.avg_marks else "—",
                "Pass":      c.pass_count,
                "Fail":      c.fail_count,
            }
            for c in courses
        ]
        print_table(rows)
        self._pause()

    # ── 6. Add ────────────────────────────────────────────────────────── #
    def _add(self) -> None:
        print_header("Add New Course")
        code     = get_input("Course Code (e.g. CS301)")
        name     = get_input("Course Name")
        sem      = get_input("Semester (1-8)")
        credits_r= input("  Credits [3]: ").strip()
        credits  = int(credits_r) if credits_r.isdigit() else 3
        max_s_r  = input("  Max Students [60]: ").strip()
        max_s    = int(max_s_r) if max_s_r.isdigit() else 60
        desc     = get_input("Description (optional)")
        dept_r   = input("  Department ID (optional): ").strip()
        dept_id  = int(dept_r) if dept_r.isdigit() else None

        if not confirm(f"Add course [{code}] {name}?"):
            print_info("Cancelled."); self._pause(); return

        course = CourseController.add(
            course_code=code, course_name=name, credits=credits,
            semester=sem, department_id=dept_id,
            description=desc, max_students=max_s,
        )
        if course:
            print_success(f"Course added! ID: {course.course_id}  [{course.course_code}]")
        else:
            print_error("Failed to add course.")
        self._pause()

    # ── 7. Update ─────────────────────────────────────────────────────── #
    def _update(self) -> None:
        print_header("Update Course")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        c = CourseController.get_by_id(cid)
        if not c:
            print_error(f"Course ID {cid} not found."); self._pause(); return

        print_info(f"Editing: [{c.course_code}] {c.course_name}")
        print_info("(Press Enter to keep current value)")
        name    = get_input("Course Name", c.course_name)
        desc    = get_input("Description", c.description)
        max_s_r = input(f"  Max Students [{c.max_students}]: ").strip()
        max_s   = int(max_s_r) if max_s_r.isdigit() else c.max_students

        ok = CourseController.update(cid, course_name=name,
                                      description=desc, max_students=max_s)
        print_success("Course updated.") if ok else print_error("Update failed.")
        self._pause()

    # ── 8. Deactivate ─────────────────────────────────────────────────── #
    def _deactivate(self) -> None:
        print_header("Deactivate Course")
        cid = self._get_course_id()
        if not cid: self._pause(); return

        c = CourseController.get_by_id(cid)
        if not c:
            print_error(f"Course ID {cid} not found."); self._pause(); return

        if not confirm(f"Deactivate [{c.course_code}] {c.course_name}?"):
            print_info("Cancelled."); self._pause(); return

        ok = CourseController.deactivate(cid)
        print_success("Course deactivated.") if ok else print_error("Failed.")
        self._pause()
