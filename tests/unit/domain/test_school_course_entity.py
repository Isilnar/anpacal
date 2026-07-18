"""
Tests unitarios del dataclass SchoolCourseEntity.

REQ-SC01: SchoolCourseEntity as Pure Dataclass
"""

import pytest

from app.domain.school_course.entities import SchoolCourseEntity


class TestSchoolCourseEntityConstruction:
    def test_construct_with_all_fields(self):
        """Scenario: Construct SchoolCourseEntity with all fields."""
        entity = SchoolCourseEntity(id=1, description="1º Primaria", status=1)
        assert entity.id == 1
        assert entity.description == "1º Primaria"
        assert entity.status == 1

    def test_no_sqlalchemy_or_flask_attributes(self):
        """Scenario: SchoolCourseEntity has no SQLAlchemy or Flask attributes."""
        entity = SchoolCourseEntity(id=1, description="2º Primaria")
        attrs = vars(entity)
        assert "_sa_instance_state" not in attrs
        assert "is_authenticated" not in attrs

    def test_default_status_is_1(self):
        entity = SchoolCourseEntity(id=1, description="Infantil")
        assert entity.status == 1

    def test_default_id_is_none(self):
        entity = SchoolCourseEntity(description="Infantil")
        assert entity.id is None

    def test_default_description_is_none(self):
        entity = SchoolCourseEntity()
        assert entity.description is None

    def test_status_0(self):
        entity = SchoolCourseEntity(id=2, description="Inactivo", status=0)
        assert entity.status == 0
