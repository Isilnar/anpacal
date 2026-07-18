"""
EarlyAttendance — domain entity.

Pure dataclass: no Flask, SQLAlchemy, or cryptography imports.
Raises ValueError if early_requested < 0 or early_plus_requested < 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class EarlyAttendance:
    """Domain entity representing a student's early-care (madrugadores) attendance."""

    student_id: int
    early_day: date
    early_requested: int
    early_plus_requested: int

    id: int | None = None
    status: int = 1
    user_id: int | None = None
    as_extra: int = 0
    not_come: int = 0
    modify_user_id: int | None = None
    modify_date: datetime | None = None
    modify_notes: str = ""

    def __post_init__(self) -> None:
        if self.early_requested < 0:
            raise ValueError("early_requested must be >= 0")
        if self.early_plus_requested < 0:
            raise ValueError("early_plus_requested must be >= 0")
