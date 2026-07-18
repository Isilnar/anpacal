"""
Mapper: convierte entre RoleORM (SQLAlchemy) y RoleEntity (domain dataclass).

Funciones puras — sin acceso a DB ni a app context.
No lazy-load: accede sólo a campos escalares (id, name, description).
"""

from __future__ import annotations

from app.domain.role.entities import RoleEntity
from app.infrastructure.role.orm import RoleORM


def orm_to_entity(orm: RoleORM) -> RoleEntity:
    """Convierte RoleORM → RoleEntity dominio (sin lazy-load)."""
    return RoleEntity(
        id=orm.id,
        name=orm.name,
        description=orm.description if orm.description is not None else "",
    )
