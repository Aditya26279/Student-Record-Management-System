"""
cli/reports_menu.py — Reports & Analytics sub-menu
"""

from __future__ import annotations

from .base_menu import BaseMenu, MenuItem
from ..services.report_service import (
    print_transcript, export_transcript_csv,
    print_department_report, print_defaulters_report,
    print_toppers_report, print_grade_distribution,
    print_system_summary,
)
from ..utils.helpers import (print_header, print_success, print_error,
                              print_info, get_input)


class ReportsMenu(BaseMenu):
    title = "Reports & Analytics"

    def __init__(self):
        super().__init__()
        self.items = [
            MenuItem("1", "System summary dashboard",         self._system_summary),
            MenuItem("2", "Department statistics",            self._dept_stats),
            MenuItem("3", "Top performers (by GPA)",          self._toppers),
            MenuItem("4", "Student transcript (console)",     self._transcript_console),
            MenuItem("5", "Student transcript (export CSV)",  self._transcript_csv),
            MenuItem("6", "Grade distribution (course)",      self._grade_dist),
            MenuItem("7", "Attendance defaulters (course)",   self._defaulters),
            MenuItem("0", "← Back to main menu",              self._go_back),
        ]

    def _system_summary(self) -> None:
        print_system_summary()
        self._pause()

    def _dept_stats(self) -> None:
        print_department_report()
        self._pause()

    def _toppers(self) -> None:
        n_r = input("  Top N students [10]: ").strip()
        n   = int(n_r) if n_r.isdigit() else 10
        print_toppers_report(n)
        self._pause()

    def _transcript_console(self) -> None:
        print_header("Student Transcript")
        sid_r = input("  Student ID: ").strip()
        if not sid_r.isdigit():
            print_error("Invalid ID."); self._pause(); return
        print_transcript(int(sid_r))
        self._pause()

    def _transcript_csv(self) -> None:
        print_header("Export Transcript to CSV")
        sid_r = input("  Student ID: ").strip()
        if not sid_r.isdigit():
            print_error("Invalid ID."); self._pause(); return
        path = export_transcript_csv(int(sid_r))
        if path:
            print_success(f"Transcript exported to:\n  {path}")
        else:
            print_error("Export failed.")
        self._pause()

    def _grade_dist(self) -> None:
        print_header("Grade Distribution")
        cid_r = input("  Course ID: ").strip()
        if not cid_r.isdigit():
            print_error("Invalid ID."); self._pause(); return
        year_r = input("  Academic year (Enter for all): ").strip()
        year   = int(year_r) if year_r.isdigit() else None
        print_grade_distribution(int(cid_r), year)
        self._pause()

    def _defaulters(self) -> None:
        print_header("Attendance Defaulters Report")
        cid_r = input("  Course ID: ").strip()
        if not cid_r.isdigit():
            print_error("Invalid ID."); self._pause(); return
        thr_r = input("  Threshold % [75]: ").strip()
        thr   = float(thr_r) if thr_r.replace(".", "").isdigit() else 75.0
        print_defaulters_report(int(cid_r), thr)
        self._pause()
