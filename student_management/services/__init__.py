# student_management/services/__init__.py
from .report_service import (
    print_transcript, export_transcript_csv,
    print_department_report, print_defaulters_report,
    print_toppers_report, print_grade_distribution,
    print_system_summary,
)

__all__ = [
    "print_transcript", "export_transcript_csv",
    "print_department_report", "print_defaulters_report",
    "print_toppers_report", "print_grade_distribution",
    "print_system_summary",
]
