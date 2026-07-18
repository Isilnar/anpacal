"""
Tests de integración: SQLAlchemySchoolCourseRepository contra SQLite in-memory.

REQ-SC04: SQLAlchemySchoolCourseRepository.get_by_id

REGLAS CRÍTICAS:
- SIN DELETE en fixtures
- SIN drop_all
- sqlalchemy_session inyectada desde fixture db
"""

import pytest

from app.domain.school_course.entities import SchoolCourseEntity
from app.infrastructure.school_course.repository import SQLAlchemySchoolCourseRepository
from tests.factories.school_course_orm_factory import SchoolCourseORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemySchoolCourseRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    """Inyecta la sesión in-memory en la factory. Sin DELETE."""
    with app.app_context():
        SchoolCourseORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestGetById:
    def test_get_by_id_returns_entity(self, repo, app):
        """Scenario: get_by_id returns SchoolCourseEntity when found."""
        with app.app_context():
            orm = SchoolCourseORMFactory.create(description="1º Primaria")

            found = repo.get_by_id(orm.id)

            assert found is not None
            assert isinstance(found, SchoolCourseEntity)
            assert found.id == orm.id
            assert found.description == "1º Primaria"

    def test_get_by_id_returns_none_when_not_found(self, repo, app):
        """Scenario: get_by_id returns None when course does not exist."""
        with app.app_context():
            result = repo.get_by_id(99999)
            assert result is None

    def test_get_by_id_maps_status(self, repo, app):
        """Scenario: status field is correctly mapped."""
        with app.app_context():
            orm = SchoolCourseORMFactory.create(description="Infantil", status=1)

            found = repo.get_by_id(orm.id)

            assert found is not None
            assert found.status == 1

    def test_get_by_id_description_preserved(self, repo, app):
        """Scenario: description is preserved exactly."""
        with app.app_context():
            orm = SchoolCourseORMFactory.create(description="3º de Primaria")

            found = repo.get_by_id(orm.id)

            assert found.description == "3º de Primaria"
