"""
models/student.py — Student data model
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Student:
    student_id:      Optional[int]   = None
    student_code:    str             = ""
    first_name:      str             = ""
    last_name:       str             = ""
    date_of_birth:   Optional[date]  = None
    gender:          str             = "Male"          # Male | Female | Other
    email:           str             = ""
    phone:           str             = ""
    address:         str             = ""
    department_id:   Optional[int]   = None
    department_name: str             = ""              # populated by JOINs
    enrollment_date: Optional[date]  = None
    status:          str             = "active"        # active|inactive|graduated|suspended
    gpa:             float           = 0.0

    # ── Derived helpers ────────────────────────────────────────────────── #
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    # ── Construct from a DB row dict ───────────────────────────────────── #
    @classmethod
    def from_row(cls, row: dict) -> "Student":
        return cls(
            student_id      = row.get("student_id"),
            student_code    = row.get("student_code", ""),
            first_name      = row.get("first_name", ""),
            last_name       = row.get("last_name", ""),
            date_of_birth   = row.get("date_of_birth"),
            gender          = row.get("gender", "Male"),
            email           = row.get("email", ""),
            phone           = row.get("phone", "") or "",
            address         = row.get("address", "") or "",
            department_id   = row.get("department_id"),
            department_name = row.get("dept_name", "") or row.get("department", "") or "",
            enrollment_date = row.get("enrollment_date"),
            status          = row.get("status", "active"),
            gpa             = float(row.get("gpa") or 0.0),
        )

    def to_dict(self) -> dict:
        return {
            "student_id":    self.student_id,
            "student_code":  self.student_code,
            "first_name":    self.first_name,
            "last_name":     self.last_name,
            "full_name":     self.full_name,
            "date_of_birth": str(self.date_of_birth) if self.date_of_birth else None,
            "gender":        self.gender,
            "email":         self.email,
            "phone":         self.phone,
            "address":       self.address,
            "department_id": self.department_id,
            "department":    self.department_name,
            "enrollment_date": str(self.enrollment_date) if self.enrollment_date else None,
            "status":        self.status,
            "gpa":           self.gpa,
        }

    def __str__(self) -> str:
        return (f"[{self.student_code}] {self.full_name} | "
                f"Dept: {self.department_name} | GPA: {self.gpa:.2f} | {self.status}")
