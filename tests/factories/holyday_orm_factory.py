"""
HolydayORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    HolydayORMFactory._meta.sqlalchemy_session = db.session
    holyday_orm = HolydayORMFactory.create(holyday=date(2026, 6, 1))
"""

from datetime import date

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.holyday.orm import HolydayORM


class HolydayORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = HolydayORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    holyday = factory.Sequence(lambda n: date(2026, 1, 1).replace(day=min(n % 28 + 1, 28)))
    status = 1
