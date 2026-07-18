"""
Tests unitarios del mapper DietIntolerance ORM → Entity.

REQ-I01: ORM alias identity (DietIntoleranceORM is DietIntolerance).
REQ-I02: orm_to_entity produce entidad completa sin atributos SQLAlchemy.
"""

from unittest.mock import MagicMock

import pytest

from app.domain.intolerance.entities import DietIntoleranceEntity
from app.infrastructure.intolerance.mapper import orm_to_entity
from app.infrastructure.intolerance.orm import DietIntoleranceORM


class TestOrmAliasIdentity:
    def test_diet_intolerance_orm_is_model(self):
        """REQ-I01: DietIntoleranceORM is defined directly in infrastructure/intolerance/orm.py."""
        assert DietIntoleranceORM.__tablename__ == "diet_intolerance"


class TestOrmToEntity:
    def _make_orm(self, id=1, description="Gluten", status=1):
        mock_orm = MagicMock(spec=DietIntoleranceORM)
        mock_orm.id = id
        mock_orm.description = description
        mock_orm.status = status
        return mock_orm

    def test_orm_to_entity_maps_all_fields(self):
        orm = self._make_orm(id=42, description="Lactosa", status=1)
        entity = orm_to_entity(orm)

        assert isinstance(entity, DietIntoleranceEntity)
        assert entity.id == 42
        assert entity.description == "Lactosa"
        assert entity.status == 1

    def test_orm_to_entity_maps_inactive(self):
        orm = self._make_orm(id=7, description="Huevo", status=0)
        entity = orm_to_entity(orm)

        assert entity.status == 0
        assert entity.is_active() is False

    def test_entity_has_no_sqlalchemy_attributes(self):
        orm = self._make_orm()
        entity = orm_to_entity(orm)

        assert not hasattr(entity, "_sa_instance_state"), (
            "orm_to_entity must return a pure domain dataclass without SA state"
        )

    def test_status_none_defaults_to_1(self):
        orm = self._make_orm(status=None)
        entity = orm_to_entity(orm)

        assert entity.status == 1
