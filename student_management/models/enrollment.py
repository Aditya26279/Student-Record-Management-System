"""
models/enrollment.py — Enrollment data model (student ↔ course mapping + grades)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# Grade table: total_marks → (letter_grade, grade_points)
GRADE_TABLE = [
    (90, "O",  10.0),
    (80, "A+",  9.0),
    (70, "A",   8.0),
    (60, "B+",  7.0),
    (50, "B",   6.0),
    (40, "C",   5.0),
    (0,  "F",   0.0),
]


def compute_grade(total: float):
    """Return (grade_letter, grade_points) for a total mark."""
    for threshold, letter, points in GRADE_TABLE:
        if total >= threshold:
            return letter, points
    return "F", 0.0


@dataclass
class Enrollment:
    enrollment_id:   Optional[int]   = None
    student_id:      Optional[int]   = None
    student_name:    str             = ""
    student_code:    str             = ""
    course_id:       Optional[int]   = None
    course_code:     str             = ""
    course_name:     str             = ""
    faculty_id:      Optional[int]   = None
    academic_year:   Optional[int]   = None
    semester:        str             = "1"
    internal_marks:  Optional[float] = None   # out of 40
    external_marks:  Optional[float] = None   # out of 60
    total_marks:     Optional[float] = None
    grade:           Optional[str]   = None
    grade_points:    Optional[float] = None
    result:          Optional[str]   = None   # Pass | Fail | Incomplete
    enrollment_date: Optional[str]   = None
    status:          str             = "enrolled"  # enrolled | dropped | completed

    @classmethod
    def from_row(cls, row: dict) -> "Enrollment":
        return cls(
            enrollment_id   = row.get("enrollment_id"),
            student_id      = row.get("student_id"),
            student_name    = row.get("student_name", "") or "",
            student_code    = row.get("student_code", "") or "",
            course_id       = row.get("course_id"),
            course_code     = row.get("course_code", "") or "",
            course_name     = row.get("course_name", "") or "",
            faculty_id      = row.get("faculty_id"),
            academic_year   = row.get("academic_year"),
            semester        = str(row.get("semester", "1")),
            internal_marks  = _float_or_none(row.get("internal_marks")),
            external_marks  = _float_or_none(row.get("external_marks")),
            total_marks     = _float_or_none(row.get("total_marks")),
            grade           = row.get("grade"),
            grade_points    = _float_or_none(row.get("grade_points")),
            result          = row.get("result"),
            enrollment_date = str(row.get("enrollment_date")) if row.get("enrollment_date") else None,
            status          = row.get("status", "enrolled"),
        )

    def to_dict(self) -> dict:
        return {
            "enrollment_id":  self.enrollment_id,
            "student_id":     self.student_id,
            "student_name":   self.student_name,
            "course_code":    self.course_code,
            "course_name":    self.course_name,
            "academic_year":  self.academic_year,
            "semester":       self.semester,
            "internal_marks": self.internal_marks,
            "external_marks": self.external_marks,
            "total_marks":    self.total_marks,
            "grade":          self.grade,
            "grade_points":   self.grade_points,
            "result":         self.result,
            "status":         self.status,
        }

    @property
    def is_passed(self) -> bool:
        return self.result == "Pass"

    def __str__(self) -> str:
        marks = f"{self.total_marks:.1f}" if self.total_marks is not None else "N/A"
        return (f"[{self.course_code}] {self.course_name} | "
                f"Marks: {marks} | Grade: {self.grade or '-'} | {self.result or 'Incomplete'}")


def _float_or_none(v) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None
