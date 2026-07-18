"""
LunchORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    LunchORMFactory._meta.sqlalchemy_session = db.session
    orm = LunchORMFactory.create(student_id=1, lunch_requested=1)
"""

from datetime import date

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.attendance.orm import LunchORM


class LunchORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = LunchORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    student_id = 1
    lunch_day = factory.Sequence(lambda n: date(2026, 1, min(n % 28 + 1, 28)))
    lunch_requested = 1
    user_id = 1
    status = 1
    as_extra = 0
    not_come = 0
    modify_notes = ""
