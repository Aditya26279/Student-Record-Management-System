"""
cli/student_menu.py — Student Management sub-menu
"""

from __future__ import annotations
from typing import Optional

from .base_menu import BaseMenu, MenuItem
from ..controllers.student_controller import StudentController
from ..utils.helpers import (print_table, print_header, print_success,
                              print_error, print_info, get_input,
                              format_gpa, confirm)


class StudentMenu(BaseMenu):
    title = "Student Management"

    def __init__(self):
        super().__init__()
        self.items = [
            MenuItem("1", "List all students",          self._list_all),
            MenuItem("2", "Search students",            self._search),
            MenuItem("3", "View student details",       self._view_detail),
            MenuItem("4", "Add new student",            self._add),
            MenuItem("5", "Update student info",        self._update),
            MenuItem("6", "Change student status",      self._change_status),
            MenuItem("7", "View top performers",        self._toppers),
            MenuItem("8", "Student statistics",         self._statistics),
            MenuItem("0", "← Back to main menu",        self._go_back),
        ]

    # ── 1. List all ───────────────────────────────────────────────────── #
    def _list_all(self) -> None:
        print_header("All Students")
        dept_id = None
        status  = input("  Filter by status (active/graduated/inactive/all) [all]: ").strip() or "all"
        if status == "all":
            status = None

        students = StudentController.get_all(status=status, department_id=dept_id)
        if not students:
            print_info("No students found.")
            self._pause(); return

        rows = [
            {
                "ID":    s.student_id,
                "Code":  s.student_code,
                "Name":  s.full_name,
                "Dept":  s.department_name or "—",
                "GPA":   f"{s.gpa:.2f}",
                "Status":s.status,
            }
            for s in students
        ]
        print_table(rows, title=f"Found {len(students)} student(s)")
        self._pause()

    # ── 2. Search ─────────────────────────────────────────────────────── #
    def _search(self) -> None:
        print_header("Search Students")
        keyword = get_input("Enter name / email / student code")
        if not keyword:
            print_error("Search keyword cannot be empty.")
            self._pause(); return

        results = StudentController.search(keyword)
        if not results:
            print_info(f"No students matching '{keyword}'.")
            self._pause(); return

        rows = [
            {
                "ID":    s.student_id,
                "Code":  s.student_code,
                "Name":  s.full_name,
                "Email": s.email,
                "GPA":   f"{s.gpa:.2f}",
                "Status":s.status,
            }
            for s in results
        ]
        print_table(rows, title=f"{len(results)} result(s) for '{keyword}'")
        self._pause()

    # ── 3. View detail ────────────────────────────────────────────────── #
    def _view_detail(self) -> None:
        print_header("Student Details")
        sid = self._get_student_id()
        if not sid:
            self._pause(); return

        s = StudentController.get_by_id(sid)
        if not s:
            print_error(f"Student ID {sid} not found.")
            self._pause(); return

        print()
        print(f"  {'ID':<20}: {s.student_id}")
        print(f"  {'Student Code':<20}: {s.student_code}")
        print(f"  {'Full Name':<20}: {s.full_name}")
        print(f"  {'Date of Birth':<20}: {s.date_of_birth}")
        print(f"  {'Gender':<20}: {s.gender}")
        print(f"  {'Email':<20}: {s.email}")
        print(f"  {'Phone':<20}: {s.phone or '—'}")
        print(f"  {'Address':<20}: {s.address or '—'}")
        print(f"  {'Department':<20}: {s.department_name or '—'}")
        print(f"  {'Enrolled On':<20}: {s.enrollment_date}")
        print(f"  {'Status':<20}: {s.status}")
        print(f"  {'GPA':<20}: {format_gpa(s.gpa)}")
        self._pause()

    # ── 4. Add ────────────────────────────────────────────────────────── #
    def _add(self) -> None:
        print_header("Add New Student")

        # Show departments
        depts = StudentController.get_departments()
        print_table(depts, title="Departments")

        first_name = get_input("First Name")
        last_name  = get_input("Last Name")
        dob        = get_input("Date of Birth (YYYY-MM-DD)")
        gender     = get_input("Gender (Male/Female/Other)", "Male")
        email      = get_input("Email")
        phone      = get_input("Phone (optional)")
        address    = get_input("Address (optional)")

        dept_raw   = input("  Department ID (optional): ").strip()
        dept_id    = int(dept_raw) if dept_raw.isdigit() else None

        print()
        print(f"  Name : {first_name} {last_name}")
        print(f"  Email: {email}  |  DOB: {dob}  |  Gender: {gender}")
        if not confirm("Confirm add student?"):
            print_info("Cancelled."); self._pause(); return

        student = StudentController.add(
            first_name=first_name, last_name=last_name,
            dob=dob, gender=gender, email=email,
            phone=phone, address=address, department_id=dept_id,
        )
        if student:
            print_success(f"Student added! Code: {student.student_code}  ID: {student.student_id}")
        else:
            print_error("Failed to add student. Check the values and try again.")
        self._pause()

    # ── 5. Update ─────────────────────────────────────────────────────── #
    def _update(self) -> None:
        print_header("Update Student")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        s = StudentController.get_by_id(sid)
        if not s:
            print_error(f"Student ID {sid} not found.")
            self._pause(); return

        print_info(f"Editing: {s.full_name} [{s.student_code}]")
        print_info("(Press Enter to keep current value)")

        first_name = get_input(f"First Name", s.first_name)
        last_name  = get_input(f"Last Name",  s.last_name)
        phone      = get_input(f"Phone",      s.phone)
        address    = get_input(f"Address",    s.address)

        ok = StudentController.update(
            sid,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
        )
        if ok:
            print_success("Student updated successfully.")
        else:
            print_error("Update failed.")
        self._pause()

    # ── 6. Change status ──────────────────────────────────────────────── #
    def _change_status(self) -> None:
        print_header("Change Student Status")
        sid = self._get_student_id()
        if not sid: self._pause(); return

        s = StudentController.get_by_id(sid)
        if not s:
            print_error(f"Student ID {sid} not found.")
            self._pause(); return

        print_info(f"Student: {s.full_name} — Current status: {s.status}")
        print("  Options: active | inactive | graduated | suspended")
        new_status = get_input("New status").strip().lower()

        if not confirm(f"Change status to '{new_status}'?"):
            print_info("Cancelled."); self._pause(); return

        ok = StudentController.change_status(sid, new_status)
        if ok:
            print_success(f"Status updated to '{new_status}'.")
        else:
            print_error("Status update failed. Check the value.")
        self._pause()

    # ── 7. Toppers ────────────────────────────────────────────────────── #
    def _toppers(self) -> None:
        print_header("Top Performers")
        n_raw = input("  How many toppers to show? [10]: ").strip()
        n     = int(n_raw) if n_raw.isdigit() else 10

        toppers = StudentController.get_topper(n)
        rows = [
            {
                "Rank": i + 1,
                "Code": t.student_code,
                "Name": t.full_name,
                "Dept": t.department_name or "—",
                "GPA":  f"{t.gpa:.2f}",
            }
            for i, t in enumerate(toppers)
        ]
        print_table(rows, title=f"Top {n} Students by GPA")
        self._pause()

    # ── 8. Statistics ─────────────────────────────────────────────────── #
    def _statistics(self) -> None:
        print_header("Student Statistics")
        stats = StudentController.get_statistics()
        print(f"  {'Total Students':<22}: {stats.get('total', 0)}")
        print(f"  {'Active':<22}: {stats.get('active', 0)}")
        print(f"  {'Graduated':<22}: {stats.get('graduated', 0)}")
        print(f"  {'Inactive/Suspended':<22}: {stats.get('inactive', 0)}")
        print(f"  {'Average GPA':<22}: {format_gpa(float(stats.get('avg_gpa') or 0))}")
        print(f"  {'Highest GPA':<22}: {format_gpa(float(stats.get('max_gpa') or 0))}")
        print(f"  {'Lowest GPA (active)':<22}: {format_gpa(float(stats.get('min_gpa') or 0))}")
        self._pause()
