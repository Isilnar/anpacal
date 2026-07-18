"""
Tests de integración: SQLAlchemyRoleRepository contra SQLite in-memory.

REQ-R03:
- test_list_all_returns_all_roles
- test_list_all_returns_role_entities
- test_list_all_ordered_by_name_asc

REGLAS CRÍTICAS:
- SIN DELETE en fixtures
- SIN drop_all
- sqlalchemy_session inyectada desde fixture db
"""

import pytest

from app.infrastructure.role.repository import SQLAlchemyRoleRepository
from tests.factories.role_orm_factory import RoleORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemyRoleRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    """Inyecta la sesión in-memory en la factory. Sin DELETE."""
    with app.app_context():
        RoleORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestListAll:
    def test_list_all_returns_role_entities(self, repo, app):
        with app.app_context():
            from app.domain.role.entities import RoleEntity

            orm = RoleORMFactory.create(name="role_integ_a", description="Integ Role A")

            result = repo.list_all()
            names = [r.name for r in result]

            assert orm.name in names
            assert all(isinstance(r, RoleEntity) for r in result)

    def test_list_all_returns_all_roles(self, repo, app):
        with app.app_context():
            RoleORMFactory.create(name="role_integ_b", description="Integ Role B")
            RoleORMFactory.create(name="role_integ_c", description="Integ Role C")

            result = repo.list_all()
            names = [r.name for r in result]

            assert "role_integ_b" in names
            assert "role_integ_c" in names

    def test_list_all_ordered_by_name_asc(self, repo, app):
        with app.app_context():
            RoleORMFactory.create(name="zzz_integ_role", description="Zzz")
            RoleORMFactory.create(name="aaa_integ_role", description="Aaa")

            result = repo.list_all()
            names = [r.name for r in result]

            # Find our specific roles and verify their relative order
            aaa_idx = next(i for i, n in enumerate(names) if n == "aaa_integ_role")
            zzz_idx = next(i for i, n in enumerate(names) if n == "zzz_integ_role")
            assert aaa_idx < zzz_idx

    def test_list_all_maps_description_correctly(self, repo, app):
        with app.app_context():
            RoleORMFactory.create(name="role_integ_desc", description="My description")

            result = repo.list_all()
            role = next((r for r in result if r.name == "role_integ_desc"), None)

            assert role is not None
            assert role.description == "My description"
