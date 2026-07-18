"""
SQLAlchemy implementations of EarlyAttendanceRepository and LunchAttendanceRepository.

Principios:
- Un solo db.session.commit() por operación de escritura.
- delete() es soft-delete (status=0), nunca borra físicamente.
- Todos los métodos de lectura retornan entidades de dominio, nunca ORM.
- list_by_school_and_date hace JOIN con Student para filtrar por school_id.
- Rangos de fecha: func.date(Column) >= str para compatibilidad SQLite.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_

from app import db
from app.domain.attendance.early_attendance import EarlyAttendance
from app.domain.attendance.lunch_attendance import LunchAttendance
from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)
from app.infrastructure.attendance.mapper import early_orm_to_domain, lunch_orm_to_domain
from app.infrastructure.attendance.orm import EarlyORM, LunchORM
from app.infrastructure.student.orm import StudentORM


class SQLAlchemyEarlyRepository(EarlyAttendanceRepository):
    def find_by_id(self, attendance_id: int) -> EarlyAttendance | None:
        orm = db.session.get(EarlyORM, attendance_id)
        return early_orm_to_domain(orm) if orm else None

    def search(
        self,
        student_id: int,
        user_student_ids: list[int],
        date_from: str,
        date_until: str,
    ) -> list[EarlyAttendance]:
        q = EarlyORM.query.filter_by(status=1)
        q = q.filter(
            func.date(EarlyORM.early_day) >= date_from,
            func.date(EarlyORM.early_day) <= date_until,
        )
        if len(user_student_ids) > 0:
            q = q.filter(EarlyORM.student_id.in_(user_student_ids))
        if student_id > 0:
            q = q.filter(EarlyORM.student_id == student_id)
        orms = q.order_by(EarlyORM.early_day).all()
        return [early_orm_to_domain(o) for o in orms]

    def find_by_student_and_date(self, student_id: int, day: date) -> EarlyAttendance | None:
        orm = (
            EarlyORM.query.filter_by(student_id=student_id, status=1)
            .filter(func.date(EarlyORM.early_day) == day)
            .first()
        )
        return early_orm_to_domain(orm) if orm else None

    def list_by_school_and_date(self, school_id: int, day: date) -> list[EarlyAttendance]:
        orms = (
            EarlyORM.query.join(StudentORM, EarlyORM.student_id == StudentORM.id)
            .filter(StudentORM.school_id == school_id)
            .filter(func.date(EarlyORM.early_day) == day)
            .filter(EarlyORM.status == 1)
            .all()
        )
        return [early_orm_to_domain(o) for o in orms]

    def list_by_student_ids_from_date(self, student_ids: list[int], from_date: date) -> list[EarlyAttendance]:
        if not student_ids:
            return []
        orms = (
            EarlyORM.query.filter(EarlyORM.status == 1)
            .filter(func.date(EarlyORM.early_day) >= from_date)
            .filter(EarlyORM.student_id.in_(student_ids))
            .order_by(EarlyORM.early_day)
            .all()
        )
        return [early_orm_to_domain(o) for o in orms]

    def list_by_date_range(
        self,
        date_from: str,
        date_until: str,
        student_id: int = 0,
        type_filter: str | None = None,
    ) -> list[EarlyAttendance]:
        if type_filter is None:
            q = EarlyORM.query.filter(or_(EarlyORM.early_requested == 1, EarlyORM.early_plus_requested == 1))
        elif type_filter == "early":
            q = EarlyORM.query.filter_by(status=1, early_requested=1)
        else:  # 'early_plus'
            q = EarlyORM.query.filter_by(status=1, early_plus_requested=1)

        if student_id > 0:
            q = q.filter(EarlyORM.student_id == student_id)

        q = q.filter(
            func.date(EarlyORM.early_day) >= date_from,
            func.date(EarlyORM.early_day) <= date_until,
        )
        orms = q.order_by(EarlyORM.early_day.desc()).all()
        return [early_orm_to_domain(o) for o in orms]

    def list_by_day(
        self,
        day: date,
        type_filter: str | None = None,
    ) -> list[EarlyAttendance]:
        if type_filter == "plus_only":
            q = EarlyORM.query.filter(EarlyORM.early_plus_requested == 1)
        else:
            q = EarlyORM.query.filter(or_(EarlyORM.early_requested == 1, EarlyORM.early_plus_requested == 1))
        orms = q.filter(func.date(EarlyORM.early_day) == day).all()
        return [early_orm_to_domain(o) for o in orms]

    def save(self, attendance: EarlyAttendance) -> EarlyAttendance:
        if attendance.id is None:
            orm = EarlyORM()
            db.session.add(orm)
        else:
            orm = db.session.get(EarlyORM, attendance.id)
            if orm is None:
                raise ValueError(f"EarlyAttendance id={attendance.id} not found")

        orm.student_id = attendance.student_id
        orm.early_day = attendance.early_day
        orm.early_requested = attendance.early_requested
        orm.early_plus_requested = attendance.early_plus_requested
        orm.status = attendance.status
        orm.user_id = attendance.user_id
        orm.as_extra = attendance.as_extra
        orm.not_come = attendance.not_come
        orm.modify_user_id = attendance.modify_user_id
        orm.modify_date = attendance.modify_date
        orm.modify_notes = attendance.modify_notes

        db.session.commit()
        db.session.refresh(orm)
        return early_orm_to_domain(orm)

    def delete(self, attendance_id: int) -> None:
        orm = db.session.get(EarlyORM, attendance_id)
        if orm is None:
            return
        orm.status = 0
        db.session.commit()


class SQLAlchemyLunchRepository(LunchAttendanceRepository):
    def find_by_id(self, attendance_id: int) -> LunchAttendance | None:
        orm = db.session.get(LunchORM, attendance_id)
        return lunch_orm_to_domain(orm) if orm else None

    def search(
        self,
        student_id: int,
        user_student_ids: list[int],
        date_from: str,
        date_until: str,
    ) -> list[LunchAttendance]:
        q = LunchORM.query.filter_by(status=1)
        q = q.filter(
            func.date(LunchORM.lunch_day) >= date_from,
            func.date(LunchORM.lunch_day) <= date_until,
        )
        if len(user_student_ids) > 0:
            q = q.filter(LunchORM.student_id.in_(user_student_ids))
        if student_id > 0:
            q = q.filter(LunchORM.student_id == student_id)
        orms = q.order_by(LunchORM.lunch_day).all()
        return [lunch_orm_to_domain(o) for o in orms]

    def find_by_student_and_date(self, student_id: int, day: date) -> LunchAttendance | None:
        orm = (
            LunchORM.query.filter_by(student_id=student_id, status=1)
            .filter(func.date(LunchORM.lunch_day) == day)
            .first()
        )
        return lunch_orm_to_domain(orm) if orm else None

    def list_by_school_and_date(self, school_id: int, day: date) -> list[LunchAttendance]:
        orms = (
            LunchORM.query.join(StudentORM, LunchORM.student_id == StudentORM.id)
            .filter(StudentORM.school_id == school_id)
            .filter(func.date(LunchORM.lunch_day) == day)
            .filter(LunchORM.status == 1)
            .all()
        )
        return [lunch_orm_to_domain(o) for o in orms]

    def list_by_student_ids_from_date(self, student_ids: list[int], from_date: date) -> list[LunchAttendance]:
        if not student_ids:
            return []
        orms = (
            LunchORM.query.filter(LunchORM.status == 1)
            .filter(func.date(LunchORM.lunch_day) >= from_date)
            .filter(LunchORM.student_id.in_(student_ids))
            .order_by(LunchORM.lunch_day)
            .all()
        )
        return [lunch_orm_to_domain(o) for o in orms]

    def list_by_date_range(
        self,
        date_from: str,
        date_until: str,
        student_id: int = 0,
    ) -> list[LunchAttendance]:
        q = LunchORM.query.filter_by(status=1, lunch_requested=1)
        if student_id > 0:
            q = q.filter(LunchORM.student_id == student_id)
        q = q.filter(
            func.date(LunchORM.lunch_day) >= date_from,
            func.date(LunchORM.lunch_day) <= date_until,
        )
        orms = q.order_by(LunchORM.lunch_day.desc()).all()
        return [lunch_orm_to_domain(o) for o in orms]

    def list_by_day(
        self,
        day: date,
        non_extra_only: bool = False,
    ) -> list[LunchAttendance]:
        q = LunchORM.query.filter(LunchORM.lunch_requested == 1)
        if non_extra_only:
            q = q.filter(or_(LunchORM.as_extra.is_(None), LunchORM.as_extra == 0))
        orms = q.filter(func.date(LunchORM.lunch_day) == day).all()
        return [lunch_orm_to_domain(o) for o in orms]

    def save(self, attendance: LunchAttendance) -> LunchAttendance:
        if attendance.id is None:
            orm = LunchORM()
            db.session.add(orm)
        else:
            orm = db.session.get(LunchORM, attendance.id)
            if orm is None:
                raise ValueError(f"LunchAttendance id={attendance.id} not found")

        orm.student_id = attendance.student_id
        orm.lunch_day = attendance.lunch_day
        orm.lunch_requested = attendance.lunch_requested
        orm.status = attendance.status
        orm.user_id = attendance.user_id
        orm.as_extra = attendance.as_extra
        orm.not_come = attendance.not_come
        orm.modify_user_id = attendance.modify_user_id
        orm.modify_date = attendance.modify_date
        orm.modify_notes = attendance.modify_notes

        db.session.commit()
        db.session.refresh(orm)
        return lunch_orm_to_domain(orm)

    def delete(self, attendance_id: int) -> None:
        orm = db.session.get(LunchORM, attendance_id)
        if orm is None:
            return
        orm.status = 0
        db.session.commit()
