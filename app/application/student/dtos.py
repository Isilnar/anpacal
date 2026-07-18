"""
DTOs (Data Transfer Objects) para el módulo Student.

Dataclasses con validación básica en __post_init__.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StudentCreateDTO:
    name: str
    surname: str
    school_id: int
    classroom: str = ""
    number_id: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    allergies: str = ""
    childish: str = ""
    brother_number: int = 0
    student_number: str = ""
    intolerance_ids: list[int] | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.surname.strip():
            raise ValueError("surname is required")
        if self.school_id <= 0:
            raise ValueError("school_id must be a positive integer")
        if self.email and "@" not in self.email:
            raise ValueError("email is invalid")
        if self.brother_number < 0:
            raise ValueError("brother_number cannot be negative")


@dataclass
class StudentEditDTO:
    student_id: int
    name: str
    surname: str
    school_id: int
    classroom: str = ""
    number_id: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    allergies: str = ""
    childish: str = ""
    brother_number: int = 0
    student_number: str = ""
    intolerance_ids: list[int] | None = None

    def __post_init__(self) -> None:
        if self.student_id <= 0:
            raise ValueError("student_id must be a positive integer")
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.surname.strip():
            raise ValueError("surname is required")
        if self.school_id <= 0:
            raise ValueError("school_id must be a positive integer")
        if self.email and "@" not in self.email:
            raise ValueError("email is invalid")
        if self.brother_number < 0:
            raise ValueError("brother_number cannot be negative")
