"""
models/course.py — Course data model
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    course_id:       Optional[int] = None
    course_code:     str           = ""
    course_name:     str           = ""
    description:     str           = ""
    credits:         int           = 3
    department_id:   Optional[int] = None
    department_name: str           = ""
    semester:        str           = "1"
    max_students:    int           = 60
    is_active:       bool          = True
    # populated from view
    enrolled_count:  int           = 0
    avg_marks:       float         = 0.0
    pass_count:      int           = 0
    fail_count:      int           = 0

    @classmethod
    def from_row(cls, row: dict) -> "Course":
        return cls(
            course_id       = row.get("course_id"),
            course_code     = row.get("course_code", ""),
            course_name     = row.get("course_name", ""),
            description     = row.get("description", "") or "",
            credits         = int(row.get("credits", 3)),
            department_id   = row.get("department_id"),
            department_name = row.get("dept_name", "") or "",
            semester        = str(row.get("semester", "1")),
            max_students    = int(row.get("max_students", 60)),
            is_active       = bool(row.get("is_active", True)),
            enrolled_count  = int(row.get("enrolled_count", 0) or 0),
            avg_marks       = float(row.get("avg_marks", 0) or 0),
            pass_count      = int(row.get("pass_count", 0) or 0),
            fail_count      = int(row.get("fail_count", 0) or 0),
        )

    def to_dict(self) -> dict:
        return {
            "course_id":      self.course_id,
            "course_code":    self.course_code,
            "course_name":    self.course_name,
            "description":    self.description,
            "credits":        self.credits,
            "department_id":  self.department_id,
            "department":     self.department_name,
            "semester":       self.semester,
            "max_students":   self.max_students,
            "is_active":      self.is_active,
            "enrolled_count": self.enrolled_count,
        }

    @property
    def seats_available(self) -> int:
        return self.max_students - self.enrolled_count

    def __str__(self) -> str:
        return (f"[{self.course_code}] {self.course_name} | "
                f"Sem: {self.semester} | Credits: {self.credits} | "
                f"Dept: {self.department_name}")
