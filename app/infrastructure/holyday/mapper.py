"""
Mapper: convierte entre HolydayORM (SQLAlchemy) y Holyday (domain dataclass).

Funciones puras — sin acceso a DB ni a app context.
Holyday no tiene campos PII → mapper trivial, sin decrypt_field.
Campo holyday es db.Date() → SQLAlchemy retorna datetime.date nativo,
no se necesita conversión.
"""

from __future__ import annotations

from app.domain.holyday.holyday import Holyday
from app.infrastructure.holyday.orm import HolydayORM


def orm_to_domain(orm: HolydayORM) -> Holyday:
    """Convierte HolydayORM → Holyday dominio (Date nativo, sin conversión)."""
    return Holyday(
        id=orm.id,
        holyday=orm.holyday,  # datetime.date nativo de SQLAlchemy
        status=orm.status if orm.status is not None else 1,
        created_at=orm.created_at,
    )


def domain_to_orm_fields(domain: Holyday) -> dict:
    """Retorna dict de campos actualizables del ORM."""
    return {
        "holyday": domain.holyday,  # datetime.date nativo
        "status": domain.status,
    }
    # created_at: gestionado por ORM (default=datetime.now), no se sobreescribe
