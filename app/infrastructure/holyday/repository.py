"""
SQLAlchemyHolydayRepository — implementación de HolydayRepository.

Principios:
- Un solo db.session.commit() por operación de escritura.
- delete() es soft-delete (status=0), nunca borra físicamente.
- Todos los métodos de lectura retornan Holyday (dominio), nunca HolydayORM.
- list_active() ordena por holyday ASC.
"""

from __future__ import annotations

from datetime import date

from app import db
from app.domain.holyday.holyday import Holyday
from app.domain.holyday.repositories import HolydayRepository
from app.infrastructure.holyday.mapper import domain_to_orm_fields, orm_to_domain
from app.infrastructure.holyday.orm import HolydayORM


class SQLAlchemyHolydayRepository(HolydayRepository):
    def find_by_id(self, holyday_id: int) -> Holyday | None:
        orm = db.session.get(HolydayORM, holyday_id)
        return orm_to_domain(orm) if orm else None

    def find_by_date(self, d: date) -> Holyday | None:
        orm = HolydayORM.query.filter_by(holyday=d).first()
        return orm_to_domain(orm) if orm else None

    def list_active(self) -> list[Holyday]:
        orms = HolydayORM.query.filter_by(status=1).order_by(HolydayORM.holyday.asc()).all()
        return [orm_to_domain(o) for o in orms]

    def save(self, holyday: Holyday) -> Holyday:
        """
        Insert o update:
        - Si holyday.id es None → nuevo registro.
        - Si holyday.id tiene valor → update del ORM existente.
        Un solo commit al final.
        """
        if holyday.id is None:
            orm = HolydayORM()
            db.session.add(orm)
        else:
            orm = db.session.get(HolydayORM, holyday.id)
            if orm is None:
                raise ValueError(f"Holyday with id={holyday.id} not found")

        fields = domain_to_orm_fields(holyday)
        for key, value in fields.items():
            setattr(orm, key, value)

        db.session.commit()
        db.session.refresh(orm)
        return orm_to_domain(orm)

    def delete(self, holyday_id: int) -> None:
        """Soft-delete: status=0. No elimina físicamente el registro."""
        orm = db.session.get(HolydayORM, holyday_id)
        if orm is None:
            return
        orm.status = 0
        db.session.commit()
