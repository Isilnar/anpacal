"""
Mapper: convierte entre SchoolORM (SQLAlchemy) y School (domain dataclass).

Funciones puras — sin acceso a DB ni a app context.
School no tiene campos PII → mapper trivial, sin decrypt_field.
"""

from __future__ import annotations

from app.domain.school.school import School
from app.infrastructure.school.orm import SchoolORM


def orm_to_domain(orm: SchoolORM) -> School:
    """Convierte SchoolORM → School dominio (plain text, sin decrypt)."""
    return School(
        id=orm.id,
        created_at=str(orm.created_at) if orm.created_at else None,
        name=orm.name or "",
        address=orm.address or "",
        phone=orm.phone or "",
        email=orm.email or "",
        status=orm.status if orm.status is not None else 1,
    )


def domain_to_orm_fields(domain: School) -> dict:
    """Retorna dict de campos actualizables del ORM."""
    return {
        "name": domain.name,
        "address": domain.address,
        "phone": domain.phone,
        "email": domain.email,
        "status": domain.status,
    }
