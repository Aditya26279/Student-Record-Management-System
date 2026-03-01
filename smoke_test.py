"""
smoke_test.py — Phase 3 backend smoke test
Run:  $env:DB_PASSWORD="12345"; python smoke_test.py
"""
import os
os.environ.setdefault("DB_PASSWORD", "12345")

from student_management.controllers import (
    StudentController, CourseController,
    EnrollmentController, AttendanceController,
)
from student_management.services import print_system_summary, print_toppers_report
from student_management.models   import Student, Course, Enrollment, Attendance

print("=" * 55)
print(" Phase 3 — Smoke Test")
print("=" * 55)

# ── imports ─────────────────────────────────────────────────
print("\n[1] All imports ... OK")

# ── statistics ───────────────────────────────────────────────
stats = StudentController.get_statistics()
print(f"\n[2] Student stats:")
print(f"     Total   : {stats.get('total', 0)}")
print(f"     Active  : {stats.get('active', 0)}")
print(f"     Avg GPA : {stats.get('avg_gpa', 0)}")

# ── get_all ──────────────────────────────────────────────────
students = StudentController.get_all(status="active")
print(f"\n[3] Active students   : {len(students)}")

# ── search ───────────────────────────────────────────────────
results = StudentController.search("meera")
print(f"\n[4] Search 'meera'    : {len(results)} match(es)")
if results:
    print(f"     → {results[0]}")

# ── courses ──────────────────────────────────────────────────
courses = CourseController.get_all()
print(f"\n[5] Active courses    : {len(courses)}")

# ── enrollments ───────────────────────────────────────────────
enrollments = EnrollmentController.get_student_enrollments(1)
print(f"\n[6] Enrollments (student 1) : {len(enrollments)}")
for e in enrollments:
    print(f"     {e}")

# ── transcript ────────────────────────────────────────────────
txn = EnrollmentController.get_transcript(1)
print(f"\n[7] Transcript (student 1):")
print(f"     CGPA         : {txn['cgpa']}")
print(f"     Pass/Fail    : {txn['pass_count']}/{txn['fail_count']}")
print(f"     Total credits: {txn['total_credits']}")

# ── attendance ────────────────────────────────────────────────
summaries = AttendanceController.get_summary(student_id=1)
print(f"\n[8] Attendance summaries (student 1): {len(summaries)}")
for s in summaries:
    print(f"     {s}")

# ── toppers ───────────────────────────────────────────────────
print()
print_toppers_report(5)

# ── system summary ────────────────────────────────────────────
print_system_summary()

print("=" * 55)
print(" All checks passed!")
print("=" * 55)
