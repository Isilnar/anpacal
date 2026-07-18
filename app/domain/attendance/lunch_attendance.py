"""
LunchAttendance — domain entity.

Pure dataclass: no Flask, SQLAlchemy, or cryptography imports.
Raises ValueError if lunch_requested < 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class LunchAttendance:
    """Domain entity representing a student's lunch-care (comedor) attendance."""

    student_id: int
    lunch_day: date
    lunch_requested: int

    id: int | None = None
    status: int = 1
    user_id: int | None = None
    as_extra: int = 0
    not_come: int = 0
    modify_user_id: int | None = None
    modify_date: datetime | None = None
    modify_notes: str = ""

    def __post_init__(self) -> None:
        if self.lunch_requested < 0:
            raise ValueError("lunch_requested must be >= 0")
