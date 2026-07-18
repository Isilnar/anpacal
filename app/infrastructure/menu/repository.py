"""
SQLAlchemyMenuRepository — implementación de MenuRepository.

Principios:
- Un solo db.session.commit() por operación de escritura.
- set_active() desactiva TODOS los activos (status=0) + inserta nuevo.
  Operación atómica: no existe ventana donde no haya menú activo.
- Todos los métodos de lectura retornan Menu (dominio), nunca MenuORM.
"""

from __future__ import annotations

from app import db
from app.domain.menu.menu import Menu
from app.domain.menu.repositories import MenuRepository
from app.infrastructure.menu.mapper import orm_to_domain
from app.infrastructure.menu.orm import MenuORM


class SQLAlchemyMenuRepository(MenuRepository):
    def get_active(self) -> Menu | None:
        orm = MenuORM.query.filter_by(status=1).first()
        return orm_to_domain(orm) if orm else None

    def set_active(self, menu_link: str) -> Menu:
        # Desactivar todos los activos
        MenuORM.query.filter_by(status=1).update({"status": 0})
        # Insertar nuevo menu activo
        new_orm = MenuORM(menu_link=menu_link, status=1)
        db.session.add(new_orm)
        db.session.commit()
        return orm_to_domain(new_orm)

    def get_by_id(self, menu_id: int) -> Menu | None:
        orm = db.session.get(MenuORM, menu_id)
        return orm_to_domain(orm) if orm else None
