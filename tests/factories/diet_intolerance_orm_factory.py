"""
DietIntoleranceORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    DietIntoleranceORMFactory._meta.sqlalchemy_session = db.session
    intol = DietIntoleranceORMFactory.create(description="Gluten")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.intolerance.orm import DietIntoleranceORM


class DietIntoleranceORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = DietIntoleranceORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    description = factory.Sequence(lambda n: f"Intolerancia {n}")
    status = 1
