"""
Attendance ORM aliases — intra-infrastructure re-exports.

Ciclo D2: StudentEarly and StudentLunch are defined in infrastructure/student/orm.py.
This module re-exports them under attendance-layer names (EarlyORM, LunchORM).
No app.models imports remain.
"""

from app.infrastructure.student.orm import StudentEarly as EarlyORM  # noqa: F401
from app.infrastructure.student.orm import StudentLunch as LunchORM  # noqa: F401

__all__ = ["EarlyORM", "LunchORM"]
