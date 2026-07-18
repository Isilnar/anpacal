"""
Tests unitarios de RoleEntity.

REQ-R01:
- RoleEntity es una dataclass pura con id, name, description
- description tiene valor por defecto vacío
- No tiene imports de Flask, SQLAlchemy ni cryptography
"""

import pytest

from app.domain.role.entities import RoleEntity


class TestRoleEntityCreation:
    def test_create_role_entity_with_all_fields(self):
        entity = RoleEntity(id=1, name="admin", description="Administrator")

        assert entity.id == 1
        assert entity.name == "admin"
        assert entity.description == "Administrator"

    def test_create_role_entity_description_defaults_to_empty(self):
        entity = RoleEntity(id=2, name="family")

        assert entity.description == ""

    def test_role_entity_has_no_sqlalchemy_attributes(self):
        entity = RoleEntity(id=1, name="admin", description="desc")

        assert not hasattr(entity, "_sa_instance_state"), "RoleEntity must be a pure domain dataclass without SA state"

    def test_role_entity_is_dataclass(self):
        from dataclasses import fields

        field_names = {f.name for f in fields(RoleEntity)}

        assert "id" in field_names
        assert "name" in field_names
        assert "description" in field_names

    def test_role_entity_equality(self):
        a = RoleEntity(id=1, name="admin", description="desc")
        b = RoleEntity(id=1, name="admin", description="desc")

        assert a == b

    def test_role_entity_inequality(self):
        a = RoleEntity(id=1, name="admin", description="desc")
        b = RoleEntity(id=2, name="family", description="other")

        assert a != b
