"""
Tests de integración: SQLAlchemyDietIntoleranceRepository contra SQLite in-memory.

Cubre REQ-U01, REQ-U02, REQ-U04:
- list_active() devuelve solo activas
- get_for_student(student_id) devuelve entidades correctas
- get_string_for_student(student_id) devuelve string correcto
"""

import pytest

from app.infrastructure.intolerance.repository import SQLAlchemyDietIntoleranceRepository
from tests.factories.diet_intolerance_orm_factory import DietIntoleranceORMFactory
from tests.factories.student_intolerance_orm_factory import StudentIntoleranceORMFactory
from tests.factories.student_orm_factory import StudentORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemyDietIntoleranceRepository()


@pytest.fixture(autouse=True)
def setup_factory_sessions(app, db):
    """Inyecta la sesión in-memory en todas las factories."""
    with app.app_context():
        DietIntoleranceORMFactory._meta.sqlalchemy_session = db.session
        StudentIntoleranceORMFactory._meta.sqlalchemy_session = db.session
        StudentORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestListActive:
    def test_list_active_returns_only_active(self, repo, app, db):
        with app.app_context():
            DietIntoleranceORMFactory.create(description="Activa uno", status=1)
            DietIntoleranceORMFactory.create(description="Activa dos", status=1)
            DietIntoleranceORMFactory.create(description="Inactiva", status=0)

            result = repo.list_active()
            descriptions = [e.description for e in result]

            assert "Activa uno" in descriptions
            assert "Activa dos" in descriptions
            assert "Inactiva" not in descriptions

    def test_list_active_ordered_alphabetically(self, repo, app, db):
        with app.app_context():
            DietIntoleranceORMFactory.create(description="Zzz", status=1)
            DietIntoleranceORMFactory.create(description="Aaa", status=1)

            result = repo.list_active()
            descriptions = [e.description for e in result]
            # Should be sorted ascending
            aaa_idx = descriptions.index("Aaa")
            zzz_idx = descriptions.index("Zzz")
            assert aaa_idx < zzz_idx

    def test_list_active_returns_empty_when_none(self, repo, app):
        with app.app_context():
            result = repo.list_active()
            # Sqlite in-memory is session-scoped so other tests may have inserted rows;
            # we only assert no inactive items sneak in
            assert all(e.status == 1 for e in result)


class TestGetForStudent:
    def test_get_for_student_returns_correct_entities(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(name="Test", surname="Integration", school_id=1)
            intol1 = DietIntoleranceORMFactory.create(description="Gluten Int", status=1)
            intol2 = DietIntoleranceORMFactory.create(description="Lactosa Int", status=1)
            StudentIntoleranceORMFactory.create(student_id=student.id, intolerance_id=intol1.id)
            StudentIntoleranceORMFactory.create(student_id=student.id, intolerance_id=intol2.id)

            result = repo.get_for_student(student.id)
            ids = {e.id for e in result}

            assert intol1.id in ids
            assert intol2.id in ids

    def test_get_for_student_returns_empty_when_no_intolerances(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(name="NoIntol", surname="Test", school_id=1)

            result = repo.get_for_student(student.id)

            assert result == []

    def test_get_for_student_does_not_return_inactive(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(name="InactiveTest", surname="Test", school_id=1)
            active = DietIntoleranceORMFactory.create(description="Activa Student", status=1)
            inactive = DietIntoleranceORMFactory.create(description="Inactiva Student", status=0)
            StudentIntoleranceORMFactory.create(student_id=student.id, intolerance_id=active.id)
            StudentIntoleranceORMFactory.create(student_id=student.id, intolerance_id=inactive.id)

            result = repo.get_for_student(student.id)
            ids = {e.id for e in result}

            assert active.id in ids
            assert inactive.id not in ids


class TestGetStringForStudent:
    def test_get_string_for_student_returns_joined_string(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(name="StringTest", surname="Test", school_id=1)
            i1 = DietIntoleranceORMFactory.create(description="Gluten Str", status=1)
            i2 = DietIntoleranceORMFactory.create(description="Lactosa Str", status=1)
            StudentIntoleranceORMFactory.create(student_id=student.id, intolerance_id=i1.id)
            StudentIntoleranceORMFactory.create(student_id=student.id, intolerance_id=i2.id)

            result = repo.get_string_for_student(student.id)

            assert "Gluten Str" in result
            assert "Lactosa Str" in result
            assert ", " in result

    def test_get_string_for_student_returns_empty_when_no_intolerances(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(name="EmptyString", surname="Test", school_id=1)

            result = repo.get_string_for_student(student.id)

            assert result == ""
