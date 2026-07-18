"""
RoleORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    RoleORMFactory._meta.sqlalchemy_session = db.session
    role_orm = RoleORMFactory.create(name="admin")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.role.orm import RoleORM


class RoleORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = RoleORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"role_{n}")
    description = factory.Sequence(lambda n: f"Role description {n}")
