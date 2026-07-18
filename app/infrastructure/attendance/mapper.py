"""
Attendance mapper: convierte entre ORM (SQLAlchemy) y entidades de dominio.

Funciones puras — no tienen acceso a DB ni a app context.
EarlyAttendance y LunchAttendance no tienen campos PII: no se usa decrypt_field.
"""

from __future__ import annotations

from datetime import date

from app.domain.attendance.early_attendance import EarlyAttendance
from app.domain.attendance.lunch_attendance import LunchAttendance
from app.infrastructure.attendance.orm import EarlyORM, LunchORM


def _to_date(value) -> date:
    """Normaliza datetime/date → date."""
    if value is None:
        return date.today()
    if hasattr(value, "date"):
        return value.date()
    return value


def early_orm_to_domain(orm: EarlyORM) -> EarlyAttendance:
    """Convierte EarlyORM → EarlyAttendance dominio."""
    return EarlyAttendance(
        id=orm.id,
        student_id=orm.student_id,
        early_day=_to_date(orm.early_day),
        early_requested=orm.early_requested or 0,
        early_plus_requested=orm.early_plus_requested or 0,
        status=orm.status if orm.status is not None else 1,
        user_id=orm.user_id,
        as_extra=orm.as_extra or 0,
        not_come=orm.not_come or 0,
        modify_user_id=orm.modify_user_id,
        modify_date=orm.modify_date,
        modify_notes=orm.modify_notes or "",
    )


def lunch_orm_to_domain(orm: LunchORM) -> LunchAttendance:
    """Convierte LunchORM → LunchAttendance dominio."""
    return LunchAttendance(
        id=orm.id,
        student_id=orm.student_id,
        lunch_day=_to_date(orm.lunch_day),
        lunch_requested=orm.lunch_requested or 0,
        status=orm.status if orm.status is not None else 1,
        user_id=orm.user_id,
        as_extra=orm.as_extra or 0,
        not_come=orm.not_come or 0,
        modify_user_id=orm.modify_user_id,
        modify_date=orm.modify_date,
        modify_notes=orm.modify_notes or "",
    )
