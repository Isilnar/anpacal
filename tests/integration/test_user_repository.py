"""
Tests de integración: SQLAlchemyUserRepository contra SQLite in-memory.

Cubre REQ-R03:
- test_save_creates_new_user
- test_save_updates_existing_user
- test_find_by_id_returns_user
- test_find_by_id_returns_none_when_not_found
- test_find_by_username_returns_user
- test_list_active_excludes_deleted_users
- test_delete_soft_deletes_user
"""

import pytest

from app.domain.user.user import User
from app.infrastructure.user.repository import SQLAlchemyUserRepository
from tests.factories.user_orm_factory import UserORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemyUserRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    """Inyecta la sesión in-memory en la factory. Sin DELETE — la sesión
    es scope=session sobre sqlite:///:memory: así que los datos no persisten
    entre ejecuciones de pytest."""
    with app.app_context():
        UserORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestSaveCreatesNewUser:
    def test_save_creates_new_user(self, repo, app):
        with app.app_context():
            user = User(username="nuevo_user", name="Ana", surname="García")
            saved = repo.save(user)

            assert saved.id is not None
            assert saved.username == "nuevo_user"
            assert saved.name == "Ana"
            assert saved.surname == "García"

    def test_save_assigns_id(self, repo, app):
        with app.app_context():
            user = User(username="user_id_test", name="X", surname="Y")
            saved = repo.save(user)
            assert isinstance(saved.id, int)
            assert saved.id > 0


class TestSaveUpdatesExistingUser:
    def test_save_updates_existing_user(self, repo, app):
        with app.app_context():
            orm = UserORMFactory.create(username="update_user", name="Antes", surname="Test")

            user = User(id=orm.id, username="update_user", name="Después", surname="Test")
            updated = repo.save(user)

            assert updated.id == orm.id
            assert updated.name == "Después"


class TestFindById:
    def test_find_by_id_returns_user(self, repo, app):
        with app.app_context():
            orm = UserORMFactory.create(username="find_user", name="Pedro", surname="López")

            found = repo.find_by_id(orm.id)

            assert found is not None
            assert found.id == orm.id
            assert found.username == "find_user"
            assert found.name == "Pedro"

    def test_find_by_id_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.find_by_id(99999)
            assert result is None


class TestFindByUsername:
    def test_find_by_username_returns_user(self, repo, app):
        with app.app_context():
            UserORMFactory.create(username="buscar_por_user", name="María", surname="X")

            found = repo.find_by_username("buscar_por_user")

            assert found is not None
            assert found.username == "buscar_por_user"
            assert found.name == "María"

    def test_find_by_username_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.find_by_username("nonexistent_xyz")
            assert result is None


class TestListActive:
    def test_list_active_excludes_deleted_users(self, repo, app):
        with app.app_context():
            UserORMFactory.create(username="activo_1", status=1)
            UserORMFactory.create(username="activo_2", status=1)
            UserORMFactory.create(username="inactivo_1", status=0)

            activos = repo.list_active()
            usernames = [u.username for u in activos]

            assert "activo_1" in usernames
            assert "activo_2" in usernames
            assert "inactivo_1" not in usernames


class TestDelete:
    def test_delete_soft_deletes_user(self, repo, app):
        with app.app_context():
            orm = UserORMFactory.create(username="borrar_user", status=1)

            repo.delete(orm.id)

            found = repo.find_by_id(orm.id)
            # find_by_id devuelve el user aunque esté borrado (soft-delete)
            assert found is not None
            assert found.status == 0

    def test_delete_user_not_in_active_list(self, repo, app):
        with app.app_context():
            orm = UserORMFactory.create(username="borrar_activo", status=1)
            repo.delete(orm.id)

            activos = repo.list_active()
            usernames = [u.username for u in activos]
            assert "borrar_activo" not in usernames
