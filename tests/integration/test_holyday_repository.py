"""
Tests de integración: SQLAlchemyHolydayRepository contra SQLite in-memory.

REQ-R03:
- test_find_by_id_returns_entity
- test_find_all_active_filters_and_orders
- test_save_creates_new_holyday
- test_save_updates_existing_holyday
- test_delete_soft_deletes

REGLAS CRÍTICAS:
- SIN DELETE en fixtures
- SIN drop_all
- sqlalchemy_session inyectada desde fixture db
"""

from datetime import date

import pytest

from app.domain.holyday.holyday import Holyday
from app.infrastructure.holyday.repository import SQLAlchemyHolydayRepository
from tests.factories.holyday_orm_factory import HolydayORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemyHolydayRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    """Inyecta la sesión in-memory en la factory. Sin DELETE."""
    with app.app_context():
        HolydayORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestFindById:
    def test_find_by_id_returns_entity(self, repo, app):
        """Scenario: find_by_id returns entity."""
        with app.app_context():
            orm = HolydayORMFactory.create(holyday=date(2026, 6, 15))

            found = repo.find_by_id(orm.id)

            assert found is not None
            assert found.id == orm.id
            assert found.holyday == date(2026, 6, 15)

    def test_find_by_id_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.find_by_id(99999)
            assert result is None


class TestFindByDate:
    def test_find_by_date_returns_entity(self, repo, app):
        with app.app_context():
            HolydayORMFactory.create(holyday=date(2026, 8, 15))

            found = repo.find_by_date(date(2026, 8, 15))

            assert found is not None
            assert found.holyday == date(2026, 8, 15)

    def test_find_by_date_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.find_by_date(date(2099, 12, 31))
            assert result is None


class TestListActive:
    def test_find_all_active_filters_and_orders(self, repo, app):
        """Scenario: find_all_active filters and orders."""
        with app.app_context():
            HolydayORMFactory.create(holyday=date(2026, 9, 10), status=1)
            HolydayORMFactory.create(holyday=date(2026, 9, 5), status=1)
            HolydayORMFactory.create(holyday=date(2026, 9, 20), status=0)

            activos = repo.list_active()
            fechas = [h.holyday for h in activos]

            assert date(2026, 9, 10) in fechas
            assert date(2026, 9, 5) in fechas
            assert date(2026, 9, 20) not in fechas

    def test_list_active_ordered_asc(self, repo, app):
        with app.app_context():
            HolydayORMFactory.create(holyday=date(2026, 10, 15), status=1)
            HolydayORMFactory.create(holyday=date(2026, 10, 1), status=1)

            activos = repo.list_active()
            fechas = [h.holyday for h in activos if h.holyday.year == 2026 and h.holyday.month == 10]

            assert fechas == sorted(fechas)


class TestSave:
    def test_save_creates_new_holyday(self, repo, app):
        """Scenario: save commits once."""
        with app.app_context():
            holyday = Holyday(holyday=date(2026, 11, 1))
            saved = repo.save(holyday)

            assert saved.id is not None
            assert saved.holyday == date(2026, 11, 1)

    def test_save_updates_existing_holyday(self, repo, app):
        with app.app_context():
            orm = HolydayORMFactory.create(holyday=date(2026, 12, 1))

            holyday = Holyday(id=orm.id, holyday=date(2026, 12, 25), status=1)
            updated = repo.save(holyday)

            assert updated.id == orm.id
            assert updated.holyday == date(2026, 12, 25)


class TestSoftDelete:
    def test_soft_delete_sets_status_0(self, repo, app):
        with app.app_context():
            orm = HolydayORMFactory.create(holyday=date(2026, 11, 11), status=1)

            repo.delete(orm.id)

            found = repo.find_by_id(orm.id)
            assert found is not None
            assert found.status == 0

    def test_soft_deleted_not_in_active_list(self, repo, app):
        with app.app_context():
            orm = HolydayORMFactory.create(holyday=date(2026, 11, 20), status=1)
            repo.delete(orm.id)

            activos = repo.list_active()
            fechas = [h.holyday for h in activos]
            assert date(2026, 11, 20) not in fechas
