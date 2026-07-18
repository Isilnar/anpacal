"""
StudentIntoleranceORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    StudentIntoleranceORMFactory._meta.sqlalchemy_session = db.session
    si = StudentIntoleranceORMFactory.create(student_id=1, intolerance_id=2)
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.intolerance.orm import StudentIntoleranceORM


class StudentIntoleranceORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = StudentIntoleranceORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    student_id = None
    intolerance_id = None
