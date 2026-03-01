"""
models/attendance.py — Attendance data model
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


VALID_STATUSES = ("Present", "Absent", "Late", "OD")


@dataclass
class Attendance:
    attendance_id: Optional[int] = None
    student_id:    Optional[int] = None
    student_name:  str           = ""
    student_code:  str           = ""
    course_id:     Optional[int] = None
    course_code:   str           = ""
    course_name:   str           = ""
    attend_date:   Optional[str] = None
    status:        str           = "Absent"     # Present | Absent | Late | OD
    remarks:       str           = ""
    marked_by:     Optional[int] = None

    @classmethod
    def from_row(cls, row: dict) -> "Attendance":
        return cls(
            attendance_id = row.get("attendance_id"),
            student_id    = row.get("student_id"),
            student_name  = row.get("student_name", "") or "",
            student_code  = row.get("student_code", "") or "",
            course_id     = row.get("course_id"),
            course_code   = row.get("course_code", "") or "",
            course_name   = row.get("course_name", "") or "",
            attend_date   = str(row.get("attend_date")) if row.get("attend_date") else None,
            status        = row.get("status", "Absent"),
            remarks       = row.get("remarks", "") or "",
            marked_by     = row.get("marked_by"),
        )

    def to_dict(self) -> dict:
        return {
            "attendance_id": self.attendance_id,
            "student_id":    self.student_id,
            "student_name":  self.student_name,
            "course_code":   self.course_code,
            "attend_date":   self.attend_date,
            "status":        self.status,
            "remarks":       self.remarks,
        }

    def __str__(self) -> str:
        return (f"[{self.attend_date}] {self.student_name} | "
                f"{self.course_code} | {self.status}")


@dataclass
class AttendanceSummary:
    """Aggregated attendance for a student in a course."""
    student_id:      Optional[int] = None
    student_code:    str           = ""
    student_name:    str           = ""
    course_id:       Optional[int] = None
    course_code:     str           = ""
    course_name:     str           = ""
    total_classes:   int           = 0
    present_count:   int           = 0
    absent_count:    int           = 0
    late_count:      int           = 0
    attendance_pct:  float         = 0.0

    @classmethod
    def from_row(cls, row: dict) -> "AttendanceSummary":
        return cls(
            student_id     = row.get("student_id"),
            student_code   = row.get("student_code", "") or "",
            student_name   = row.get("student_name", "") or "",
            course_id      = row.get("course_id"),
            course_code    = row.get("course_code", "") or "",
            course_name    = row.get("course_name", "") or "",
            total_classes  = int(row.get("total_classes", 0) or 0),
            present_count  = int(row.get("present_count", 0) or 0),
            absent_count   = int(row.get("absent_count", 0) or 0),
            late_count     = int(row.get("late_count", 0) or 0),
            attendance_pct = float(row.get("attendance_pct", 0) or 0),
        )

    @property
    def is_eligible(self) -> bool:
        """Students need >= 75 % attendance to be eligible for exams."""
        return self.attendance_pct >= 75.0

    def __str__(self) -> str:
        flag = "✓ Eligible" if self.is_eligible else "✗ Shortage"
        return (f"{self.course_code}: {self.present_count}/{self.total_classes} "
                f"({self.attendance_pct:.1f}%) — {flag}")
