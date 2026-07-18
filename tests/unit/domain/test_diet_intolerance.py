"""
Tests unitarios de la entidad DietIntoleranceEntity.

REQ-D01:
- Entity es dataclass con campos accesibles por nombre
- is_active() devuelve True cuando status==1
- is_active() devuelve False cuando status==0
- No tiene atributos de SQLAlchemy (_sa_instance_state)
"""

import pytest

from app.domain.intolerance.entities import DietIntoleranceEntity


class TestDietIntoleranceEntityFields:
    def test_fields_accessible_by_name(self):
        entity = DietIntoleranceEntity(id=1, description="Gluten", status=1)
        assert entity.id == 1
        assert entity.description == "Gluten"
        assert entity.status == 1

    def test_status_defaults_to_1(self):
        entity = DietIntoleranceEntity(id=2, description="Lactosa")
        assert entity.status == 1

    def test_no_sqlalchemy_attributes(self):
        entity = DietIntoleranceEntity(id=3, description="Frutos secos", status=1)
        assert not hasattr(entity, "_sa_instance_state"), "DietIntoleranceEntity must not carry SQLAlchemy state"


class TestDietIntoleranceIsActive:
    def test_is_active_returns_true_when_status_1(self):
        entity = DietIntoleranceEntity(id=1, description="Gluten", status=1)
        assert entity.is_active() is True

    def test_is_active_returns_false_when_status_0(self):
        entity = DietIntoleranceEntity(id=2, description="Lactosa", status=0)
        assert entity.is_active() is False

    def test_is_active_returns_false_when_status_other(self):
        entity = DietIntoleranceEntity(id=3, description="Huevo", status=2)
        assert entity.is_active() is False
