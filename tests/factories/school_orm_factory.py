"""
SchoolORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    SchoolORMFactory._meta.sqlalchemy_session = db.session
    school_orm = SchoolORMFactory.create(name="Colexio A", address="Rúa 1")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.school.orm import SchoolORM


class SchoolORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SchoolORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Colexio {n}")
    address = factory.Sequence(lambda n: f"Rúa {n}, Santiago")
    phone = ""
    email = ""
    status = 1
