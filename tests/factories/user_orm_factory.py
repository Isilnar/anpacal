"""
UserORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    UserORMFactory._meta.sqlalchemy_session = db.session
    user_orm = UserORMFactory.create(username="pepe")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.user.orm import UserORM


class UserORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = UserORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user_{n}")
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    email = ""  # vacío: los tests de integración lo setean si hace falta PII
    phone = ""
    number_id = ""
    email_hash = ""
    number_id_hash = ""
    address = ""
    status = 1
    user_partner = ""
    ws_token = None
    password = "hashed_password_placeholder"
