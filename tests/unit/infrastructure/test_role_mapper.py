"""
Tests unitarios del mapper Role ORM → Entity.

REQ-I01: ORM alias identity (RoleORM is Role).
REQ-I02: orm_to_entity produce entidad completa sin atributos SQLAlchemy.
"""

from unittest.mock import MagicMock

import pytest

from app.domain.role.entities import RoleEntity
from app.infrastructure.role.mapper import orm_to_entity
from app.infrastructure.role.orm import RoleORM


class TestOrmAliasIdentity:
    def test_role_orm_is_model(self):
        """REQ-I01: RoleORM is defined directly in infrastructure/role/orm.py."""
        assert RoleORM.__tablename__ == "role"


class TestOrmToEntity:
    def _make_orm(self, id=1, name="admin", description="Administrator"):
        mock_orm = MagicMock(spec=RoleORM)
        mock_orm.id = id
        mock_orm.name = name
        mock_orm.description = description
        return mock_orm

    def test_orm_to_entity_maps_all_fields(self):
        orm = self._make_orm(id=42, name="family", description="Family role")
        entity = orm_to_entity(orm)

        assert isinstance(entity, RoleEntity)
        assert entity.id == 42
        assert entity.name == "family"
        assert entity.description == "Family role"

    def test_orm_to_entity_description_none_defaults_to_empty(self):
        orm = self._make_orm(description=None)
        entity = orm_to_entity(orm)

        assert entity.description == ""

    def test_entity_has_no_sqlalchemy_attributes(self):
        orm = self._make_orm()
        entity = orm_to_entity(orm)

        assert not hasattr(entity, "_sa_instance_state"), (
            "orm_to_entity must return a pure domain dataclass without SA state"
        )

    def test_orm_to_entity_maps_id_correctly(self):
        orm = self._make_orm(id=99)
        entity = orm_to_entity(orm)

        assert entity.id == 99

    def test_orm_to_entity_maps_name_correctly(self):
        orm = self._make_orm(name="lunchcare")
        entity = orm_to_entity(orm)

        assert entity.name == "lunchcare"
