"""
SQLAlchemyDietIntoleranceRepository — implementación de DietIntoleranceRepository.

Principios:
- Todos los métodos de lectura retornan DietIntoleranceEntity (dominio), nunca ORM.
- list_active() ordena por description ASC.
- get_for_student() hace JOIN con StudentIntoleranceORM, filtra status==1.
- get_string_for_student() delega a get_for_student() — sin SQL adicional.
"""

from __future__ import annotations

from app import db
from app.domain.intolerance.entities import DietIntoleranceEntity
from app.domain.intolerance.repositories import DietIntoleranceRepository
from app.infrastructure.intolerance.mapper import orm_to_entity
from app.infrastructure.intolerance.orm import DietIntoleranceORM, StudentIntoleranceORM


class SQLAlchemyDietIntoleranceRepository(DietIntoleranceRepository):
    def list_active(self) -> list[DietIntoleranceEntity]:
        orms = DietIntoleranceORM.query.filter_by(status=1).order_by(DietIntoleranceORM.description.asc()).all()
        return [orm_to_entity(o) for o in orms]

    def get_by_id(self, id: int) -> DietIntoleranceEntity | None:
        orm = db.session.get(DietIntoleranceORM, id)
        return orm_to_entity(orm) if orm else None

    def get_for_student(self, student_id: int) -> list[DietIntoleranceEntity]:
        orms = (
            DietIntoleranceORM.query.join(
                StudentIntoleranceORM, StudentIntoleranceORM.intolerance_id == DietIntoleranceORM.id
            )
            .filter(
                StudentIntoleranceORM.student_id == student_id,
                DietIntoleranceORM.status == 1,
            )
            .order_by(DietIntoleranceORM.description.asc())
            .all()
        )
        return [orm_to_entity(o) for o in orms]
