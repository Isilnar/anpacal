"""
Mapper: convierte entre SchoolCourseORM (SQLAlchemy) y SchoolCourseEntity (domain dataclass).

Funciones puras — sin acceso a DB ni a app context.
"""

from __future__ import annotations

from app.domain.school_course.entities import SchoolCourseEntity
from app.infrastructure.school_course.orm import SchoolCourseORM


def orm_to_entity(orm: SchoolCourseORM) -> SchoolCourseEntity:
    """Convierte SchoolCourseORM → SchoolCourseEntity dominio."""
    return SchoolCourseEntity(
        id=orm.id,
        description=orm.description,
        status=orm.status if orm.status is not None else 1,
    )
