"""
StudentORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    StudentORMFactory._meta.sqlalchemy_session = db.session
    student_orm = StudentORMFactory.create(name="Ana", surname="García")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.student.orm import StudentORM


class StudentORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = StudentORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    school_id = 1
    classroom = factory.Sequence(lambda n: f"1-{n}A")
    number_id = ""  # vacío: los tests de integración lo setean si hace falta PII
    number_id_hash = ""
    phone = ""
    email = ""
    address = ""
    allergies = ""
    status = 1
    childish = "no"
    brother_number = 0
    student_number = ""
