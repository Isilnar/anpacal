"""
Tests de integración para métodos get_dict() en ORM classes con callers reales.

Cubre:
- SchoolORM.get_dict() — usado en school_routes.py
- HolydayORM.get_dict() — usado en holyday_routes.py
"""

from datetime import date as Date

import pytest


@pytest.fixture(autouse=True)
def setup_factories(app, db):
    """Set factory sessions to in-memory DB."""
    with app.app_context():
        from tests.factories.holyday_orm_factory import HolydayORMFactory
        from tests.factories.school_orm_factory import SchoolORMFactory

        SchoolORMFactory._meta.sqlalchemy_session = db.session
        HolydayORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestSchoolORMGetDict:
    def test_get_dict_returns_expected_keys(self, app, db):
        from tests.factories.school_orm_factory import SchoolORMFactory

        with app.app_context():
            orm = SchoolORMFactory.create(
                name="CEIP Test", address="Rúa Test", phone="981000000", email="test@test.com"
            )
            result = orm.get_dict()
            assert result["id"] == orm.id
            assert result["name"] == "CEIP Test"
            assert result["address"] == "Rúa Test"
            assert result["phone"] == "981000000"
            assert result["email"] == "test@test.com"
            assert "status" in result


class TestHolydayORMGetDict:
    def test_get_dict_returns_expected_keys(self, app, db):
        from tests.factories.holyday_orm_factory import HolydayORMFactory

        with app.app_context():
            orm = HolydayORMFactory.create(holyday=Date(2026, 6, 15))
            result = orm.get_dict()
            assert result["id"] == orm.id
            assert result["holyday"] == Date(2026, 6, 15)
            assert result["holyday_formated"] == "15/06/2026"
            assert "status" in result
