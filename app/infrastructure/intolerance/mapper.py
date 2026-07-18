"""
Mapper: convierte entre DietIntoleranceORM (SQLAlchemy) y DietIntoleranceEntity (domain dataclass).

Funciones puras — sin acceso a DB ni a app context.
No lazy-load: accede sólo a campos escalares (id, description, status).
"""

from __future__ import annotations

from app.domain.intolerance.entities import DietIntoleranceEntity
from app.infrastructure.intolerance.orm import DietIntoleranceORM


def orm_to_entity(orm: DietIntoleranceORM) -> DietIntoleranceEntity:
    """Convierte DietIntoleranceORM → DietIntoleranceEntity dominio (sin lazy-load)."""
    return DietIntoleranceEntity(
        id=orm.id,
        description=orm.description,
        status=orm.status if orm.status is not None else 1,
    )
