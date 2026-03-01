"""
services/report_service.py — Report generation (console, CSV, PDF)
"""

from __future__ import annotations
import os
import csv
from datetime import datetime
from typing import List, Optional

from ..config.database          import execute_query
from ..controllers.student_controller    import StudentController
from ..controllers.enrollment_controller import EnrollmentController
from ..controllers.attendance_controller import AttendanceController
from ..utils.logger             import setup_logger
from ..utils.helpers            import (print_table, print_header,
                                        format_gpa, format_result,
                                        format_attendance_pct)

log = setup_logger("report_svc")

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def _ensure_reports_dir() -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR


# ══════════════════════════════════════════════════════════════════════════════
# STUDENT TRANSCRIPT
# ══════════════════════════════════════════════════════════════════════════════

def print_transcript(student_id: int) -> None:
    student = StudentController.get_by_id(student_id)
    if not student:
        log.error("Student %d not found", student_id)
        return

    print_header(f"ACADEMIC TRANSCRIPT — {student.full_name}")
    print(f"  Code       : {student.student_code}")
    print(f"  Department : {student.department_name}")
    print(f"  Status     : {student.status}")
    print(f"  GPA        : {format_gpa(student.gpa)}")
    print()

    enrollments = EnrollmentController.get_student_enrollments(student_id)
    rows = [
        {
            "Course": e.course_code,
            "Name":   e.course_name[:30],
            "Sem":    e.semester,
            "Year":   e.academic_year,
            "Int":    f"{e.internal_marks:.1f}" if e.internal_marks is not None else "—",
            "Ext":    f"{e.external_marks:.1f}" if e.external_marks is not None else "—",
            "Total":  f"{e.total_marks:.1f}"    if e.total_marks    is not None else "—",
            "Grade":  e.grade or "—",
            "Result": e.result or "Incomplete",
        }
        for e in enrollments
    ]
    print_table(rows, title="Enrollment & Marks")

    # Attendance
    att_summaries = AttendanceController.get_summary(student_id=student_id)
    if att_summaries:
        att_rows = [
            {
                "Course": s.course_code,
                "Total":  s.total_classes,
                "Present":s.present_count,
                "Absent": s.absent_count,
                "Late":   s.late_count,
                "Attend%":f"{s.attendance_pct:.1f}%",
                "Eligible": "Yes" if s.is_eligible else "NO ⚠",
            }
            for s in att_summaries
        ]
        print_table(att_rows, title="Attendance Summary")


def export_transcript_csv(student_id: int) -> Optional[str]:
    student = StudentController.get_by_id(student_id)
    if not student:
        return None

    _ensure_reports_dir()
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"transcript_{student.student_code}_{ts}.csv")

    enrollments = EnrollmentController.get_student_enrollments(student_id)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Student Record Management System — Transcript"])
        w.writerow(["Name", student.full_name])
        w.writerow(["Code", student.student_code])
        w.writerow(["Department", student.department_name])
        w.writerow(["GPA", student.gpa])
        w.writerow([])
        w.writerow(["Course Code", "Course Name", "Semester", "Year",
                    "Internal", "External", "Total", "Grade", "Result"])
        for e in enrollments:
            w.writerow([e.course_code, e.course_name, e.semester, e.academic_year,
                        e.internal_marks, e.external_marks, e.total_marks,
                        e.grade, e.result])

    log.info("Transcript CSV → %s", path)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# DEPARTMENT REPORT
# ══════════════════════════════════════════════════════════════════════════════

def print_department_report() -> None:
    print_header("DEPARTMENT STATISTICS")
    rows = execute_query(
        """SELECT d.dept_code, d.dept_name,
                  COUNT(DISTINCT s.student_id)       AS total_students,
                  SUM(s.status='active')             AS active,
                  ROUND(AVG(s.gpa),2)                AS avg_gpa,
                  COUNT(DISTINCT c.course_id)        AS courses
           FROM departments d
           LEFT JOIN students s ON d.department_id = s.department_id
           LEFT JOIN courses  c ON d.department_id = c.department_id
           GROUP BY d.dept_code, d.dept_name
           ORDER BY d.dept_name"""
    )
    print_table(rows)


# ══════════════════════════════════════════════════════════════════════════════
# ATTENDANCE DEFAULTERS REPORT
# ══════════════════════════════════════════════════════════════════════════════

def print_defaulters_report(course_id: int, threshold: float = 75.0) -> None:
    defaulters = AttendanceController.get_defaulters(course_id, threshold)
    print_header(f"ATTENDANCE DEFAULTERS — Course {course_id}  (< {threshold}%)")
    if not defaulters:
        print("  No defaulters found.\n")
        return
    rows = [
        {
            "Student Code": d.student_code,
            "Student Name": d.student_name,
            "Course":       d.course_code,
            "Total":        d.total_classes,
            "Present":      d.present_count,
            "Attend%":      f"{d.attendance_pct:.1f}%",
            "Shortage":     f"{max(0, threshold - d.attendance_pct):.1f}%",
        }
        for d in defaulters
    ]
    print_table(rows)


# ══════════════════════════════════════════════════════════════════════════════
# TOP PERFORMERS
# ══════════════════════════════════════════════════════════════════════════════

def print_toppers_report(limit: int = 10) -> None:
    print_header(f"TOP {limit} STUDENTS BY GPA")
    students = StudentController.get_topper(limit)
    rows = [
        {
            "Rank":  i + 1,
            "Code":  s.student_code,
            "Name":  s.full_name,
            "Dept":  s.department_name,
            "GPA":   s.gpa,
        }
        for i, s in enumerate(students)
    ]
    print_table(rows)


# ══════════════════════════════════════════════════════════════════════════════
# COURSE GRADE DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════

def print_grade_distribution(course_id: int,
                              academic_year: Optional[int] = None) -> None:
    dist = EnrollmentController.grade_distribution(course_id, academic_year)
    print_header(f"GRADE DISTRIBUTION — Course ID {course_id}")
    print_table(dist)


# ══════════════════════════════════════════════════════════════════════════════
# FULL SYSTEM STATS
# ══════════════════════════════════════════════════════════════════════════════

def print_system_summary() -> None:
    print_header("SYSTEM SUMMARY")
    stats = StudentController.get_statistics()
    print(f"  Total Students  : {stats.get('total', 0)}")
    print(f"  Active          : {stats.get('active', 0)}")
    print(f"  Graduated       : {stats.get('graduated', 0)}")
    print(f"  Inactive        : {stats.get('inactive', 0)}")
    print(f"  Average GPA     : {format_gpa(float(stats.get('avg_gpa', 0) or 0))}")
    print(f"  Highest GPA     : {format_gpa(float(stats.get('max_gpa', 0) or 0))}")
    print()
    print_department_report()
