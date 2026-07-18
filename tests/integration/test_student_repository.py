"""
Tests de integración: SQLAlchemyStudentRepository contra SQLite in-memory.

Cubre REQ-R01 + REQ-R03:
- test_save_creates_new_student
- test_save_updates_existing_student
- test_find_by_id_returns_student
- test_find_by_id_returns_none_when_not_found
- test_list_active_excludes_deleted
- test_delete_soft_deletes_student
- test_sync_intolerances_adds_and_removes
"""

import pytest

from app.domain.student.student import Student
from app.infrastructure.student.repository import SQLAlchemyStudentRepository
from tests.factories.student_orm_factory import StudentORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemyStudentRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    """Inyecta la sesión in-memory en la factory. Sin DELETE — la sesión
    es scope=session sobre sqlite:///:memory: así que los datos no persisten
    entre ejecuciones de pytest."""
    with app.app_context():
        StudentORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestSaveCreatesNewStudent:
    def test_save_creates_new_student(self, repo, app):
        with app.app_context():
            student = Student(name="Ana", surname="García", school_id=1)
            saved = repo.save(student)

            assert saved.id is not None
            assert saved.name == "Ana"
            assert saved.surname == "García"
            assert saved.school_id == 1

    def test_save_assigns_id(self, repo, app):
        with app.app_context():
            student = Student(name="Luis", surname="Pérez", school_id=1)
            saved = repo.save(student)
            assert isinstance(saved.id, int)
            assert saved.id > 0


class TestSaveUpdatesExistingStudent:
    def test_save_updates_existing_student(self, repo, app):
        with app.app_context():
            orm = StudentORMFactory.create(name="Antes", surname="Test", school_id=1)

            student = Student(id=orm.id, name="Después", surname="Test", school_id=1)
            updated = repo.save(student)

            assert updated.id == orm.id
            assert updated.name == "Después"


class TestGetById:
    def test_find_by_id_returns_student(self, repo, app):
        with app.app_context():
            orm = StudentORMFactory.create(name="Pedro", surname="López", school_id=1)

            found = repo.get_by_id(orm.id)

            assert found is not None
            assert found.id == orm.id
            assert found.name == "Pedro"
            assert found.surname == "López"

    def test_find_by_id_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.get_by_id(99999)
            assert result is None

    def test_find_by_id_alias_works(self, repo, app):
        """find_by_id es alias de get_by_id — usado por use cases de reports."""
        with app.app_context():
            orm = StudentORMFactory.create(name="Ana", surname="García", school_id=1)

            found = repo.find_by_id(orm.id)

            assert found is not None
            assert found.id == orm.id
            assert found.name == "Ana"


class TestListActive:
    def test_list_active_excludes_deleted(self, repo, app):
        with app.app_context():
            StudentORMFactory.create(name="Activo1", surname="Test", school_id=1, status=1)
            StudentORMFactory.create(name="Activo2", surname="Test", school_id=1, status=1)
            StudentORMFactory.create(name="Inactivo", surname="Test", school_id=1, status=0)

            activos = repo.list_active()
            nombres = [s.name for s in activos]

            assert "Activo1" in nombres
            assert "Activo2" in nombres
            assert "Inactivo" not in nombres


class TestSoftDelete:
    def test_delete_soft_deletes_student(self, repo, app):
        with app.app_context():
            orm = StudentORMFactory.create(name="Borrar", surname="Test", school_id=1, status=1)

            repo.soft_delete(orm.id)

            found = repo.get_by_id(orm.id)
            assert found is not None
            assert found.status == 0

    def test_deleted_student_not_in_active_list(self, repo, app):
        with app.app_context():
            orm = StudentORMFactory.create(name="BorrarActivo", surname="Test", school_id=1, status=1)
            repo.soft_delete(orm.id)

            activos = repo.list_active()
            nombres = [s.name for s in activos]
            assert "BorrarActivo" not in nombres


class TestSyncIntolerances:
    def test_sync_intolerances_adds_new(self, repo, app, db):
        with app.app_context():
            from app.infrastructure.intolerance.orm import (
                DietIntoleranceORM as DietIntolerance,  # Create diet intolerances in DB first
            )

            d1 = DietIntolerance(description="Gluten", status=1)
            d2 = DietIntolerance(description="Lactosa", status=1)
            db.session.add(d1)
            db.session.add(d2)
            db.session.commit()

            orm = StudentORMFactory.create(name="SyncTest", surname="Test", school_id=1)
            repo.sync_intolerances(orm.id, [d1.id, d2.id])

            found = repo.get_by_id(orm.id)
            assert set(found.intolerance_ids) == {d1.id, d2.id}

            # cleanup diet intolerances
            db.session.delete(d1)
            db.session.delete(d2)
            db.session.commit()

    def test_sync_intolerances_removes_old(self, repo, app, db):
        with app.app_context():
            from app.infrastructure.intolerance.orm import DietIntoleranceORM as DietIntolerance
            from app.infrastructure.intolerance.orm import StudentIntoleranceORM as StudentIntolerance

            d1 = DietIntolerance(description="Gluten2", status=1)
            d2 = DietIntolerance(description="Lactosa2", status=1)
            db.session.add_all([d1, d2])
            db.session.commit()

            orm = StudentORMFactory.create(name="SyncRemove", surname="Test", school_id=1)
            # Add both first
            db.session.add(StudentIntolerance(student_id=orm.id, intolerance_id=d1.id))
            db.session.add(StudentIntolerance(student_id=orm.id, intolerance_id=d2.id))
            db.session.commit()

            # Now sync with only d1 — d2 should be removed
            repo.sync_intolerances(orm.id, [d1.id])

            found = repo.get_by_id(orm.id)
            assert found.intolerance_ids == [d1.id]
            # No cleanup needed — sqlite:///:memory: se limpia sola entre sesiones pytest
