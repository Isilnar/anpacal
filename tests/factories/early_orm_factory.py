"""
EarlyORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    EarlyORMFactory._meta.sqlalchemy_session = db.session
    orm = EarlyORMFactory.create(student_id=1, early_requested=1)
"""

from datetime import date

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.attendance.orm import EarlyORM


class EarlyORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = EarlyORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    student_id = 1
    early_day = factory.Sequence(lambda n: date(2026, 1, min(n % 28 + 1, 28)))
    early_requested = 1
    early_plus_requested = 0
    user_id = 1
    status = 1
    as_extra = 0
    not_come = 0
    modify_notes = ""
