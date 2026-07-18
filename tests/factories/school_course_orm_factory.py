"""
SchoolCourseORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    SchoolCourseORMFactory._meta.sqlalchemy_session = db.session
    course_orm = SchoolCourseORMFactory.create(description="1º Primaria")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.school_course.orm import SchoolCourseORM


class SchoolCourseORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SchoolCourseORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    description = factory.Sequence(lambda n: f"Curso {n}")
    status = 1
