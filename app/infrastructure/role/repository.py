"""
SQLAlchemyRoleRepository — implementación de RoleRepository.

Principios:
- Todos los métodos de lectura retornan RoleEntity (dominio), nunca ORM.
- list_all() retorna todos los roles sin filtro de status (Role no tiene status).
- Ordenados por name ASC.
"""

from __future__ import annotations

from app.domain.role.entities import RoleEntity
from app.domain.role.repositories import RoleRepository
from app.infrastructure.role.mapper import orm_to_entity
from app.infrastructure.role.orm import RoleORM


class SQLAlchemyRoleRepository(RoleRepository):
    def list_all(self) -> list[RoleEntity]:
        orms = RoleORM.query.order_by(RoleORM.name.asc()).all()
        return [orm_to_entity(o) for o in orms]
