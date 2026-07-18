"""
Tests unitarios: SchoolCourseMapper — funciones puras, sin DB.

REQ-SC02: ORM → Entity Mapper
"""

from unittest.mock import MagicMock

import pytest

from app.domain.school_course.entities import SchoolCourseEntity
from app.infrastructure.school_course.mapper import orm_to_entity
from app.infrastructure.school_course.orm import SchoolCourseORM


class TestSchoolCourseORMAlias:
    def test_alias_resolves_to_existing_model(self):
        """Scenario: SchoolCourseORM is defined directly in infrastructure/school_course/orm.py."""
        assert SchoolCourseORM.__tablename__ == "school_courses"


class TestSchoolCourseMapper:
    def _make_mock_orm(self, id=1, description="1º Primaria", status=1):
        orm = MagicMock()
        orm.id = id
        orm.description = description
        orm.status = status
        return orm

    def test_orm_to_entity_maps_fields(self):
        """Scenario: orm_to_entity maps all fields correctly."""
        orm = self._make_mock_orm(id=1, description="2º Primaria", status=1)
        entity = orm_to_entity(orm)

        assert entity.id == 1
        assert entity.description == "2º Primaria"
        assert entity.status == 1

    def test_orm_to_entity_returns_school_course_entity(self):
        orm = self._make_mock_orm()
        entity = orm_to_entity(orm)
        assert isinstance(entity, SchoolCourseEntity)

    def test_status_defaults_to_1_when_none(self):
        """Scenario: status defaults to 1 when ORM returns None."""
        orm = self._make_mock_orm(status=None)
        entity = orm_to_entity(orm)
        assert entity.status == 1

    def test_description_preserved(self):
        orm = self._make_mock_orm(description="Infantil 3 anos")
        entity = orm_to_entity(orm)
        assert entity.description == "Infantil 3 anos"

    def test_description_none_preserved(self):
        orm = self._make_mock_orm(description=None)
        entity = orm_to_entity(orm)
        assert entity.description is None
