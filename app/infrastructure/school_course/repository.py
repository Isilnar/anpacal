"""
SQLAlchemySchoolCourseRepository — implementación de SchoolCourseRepository.

Solo lectura: get_by_id devuelve SchoolCourseEntity (dominio), nunca SchoolCourseORM.
"""

from __future__ import annotations

from app import db
from app.domain.school_course.entities import SchoolCourseEntity
from app.domain.school_course.repositories import SchoolCourseRepository
from app.infrastructure.school_course.mapper import orm_to_entity
from app.infrastructure.school_course.orm import SchoolCourseORM


class SQLAlchemySchoolCourseRepository(SchoolCourseRepository):
    def get_by_id(self, course_id: int) -> SchoolCourseEntity | None:
        orm = db.session.get(SchoolCourseORM, course_id)
        return orm_to_entity(orm) if orm else None

    def list_all(self) -> list[SchoolCourseEntity]:
        rows = db.session.query(SchoolCourseORM).order_by(SchoolCourseORM.id).all()
        return [orm_to_entity(r) for r in rows]
