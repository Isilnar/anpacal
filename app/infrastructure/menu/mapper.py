"""
Mapper: convierte entre MenuORM (SQLAlchemy) y Menu (domain dataclass).

Funciones puras — sin acceso a DB ni a app context.
Menu no tiene campos PII → mapper trivial, sin decrypt_field.
"""

from __future__ import annotations

from app.domain.menu.menu import Menu
from app.infrastructure.menu.orm import MenuORM


def orm_to_domain(orm: MenuORM) -> Menu:
    """Convierte MenuORM → Menu dominio (plain text, sin decrypt)."""
    return Menu(
        id=orm.id,
        menu_link=orm.menu_link or "",
        status=orm.status if orm.status is not None else 1,
        created_at=orm.created_at,
    )


def domain_to_orm_fields(domain: Menu) -> dict:
    """Retorna dict de campos actualizables del ORM."""
    return {
        "menu_link": domain.menu_link,
        "status": domain.status,
    }
