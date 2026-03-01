"""
cli/main_menu.py — Application root menu
"""

from __future__ import annotations

from .base_menu       import BaseMenu, MenuItem
from .student_menu    import StudentMenu
from .course_menu     import CourseMenu
from .enrollment_menu import EnrollmentMenu
from .attendance_menu import AttendanceMenu
from .reports_menu    import ReportsMenu
from ..utils.helpers  import print_header, print_info


class MainMenu(BaseMenu):
    title = "Main Menu"

    def __init__(self):
        super().__init__()
        self._student_menu    = StudentMenu()
        self._course_menu     = CourseMenu()
        self._enrollment_menu = EnrollmentMenu()
        self._attendance_menu = AttendanceMenu()
        self._reports_menu    = ReportsMenu()

        self.items = [
            MenuItem("1", "👤  Student Management",        self._student_menu.run),
            MenuItem("2", "📚  Course Management",         self._course_menu.run),
            MenuItem("3", "📋  Enrollment & Marks",        self._enrollment_menu.run),
            MenuItem("4", "📅  Attendance Management",     self._attendance_menu.run),
            MenuItem("5", "📊  Reports & Analytics",       self._reports_menu.run),
            MenuItem("0", "🚪  Exit",                      self._exit),
        ]

    def _print_menu(self) -> None:
        self._print_banner()
        print_header(self.title)
        for item in self.items:
            print(f"  \033[1;33m[{item.key}]\033[0m  {item.label}")
        print()

def main() -> None:
    menu = MainMenu()
    menu.run()