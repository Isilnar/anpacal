"""
Mapper: convierte entre UserORM (SQLAlchemy) y User (domain dataclass).

Funciones puras — no tienen acceso a DB ni a app context.
La desencriptación de PII la hace el mapper porque el dominio recibe
siempre valores en claro (principio: el dominio trabaja con datos reales).
"""

from app.domain.user.user import User
from app.infrastructure.crypto import decrypt_field


def orm_to_domain(orm) -> User:
    """Convierte UserORM → User dominio (con campos PII desencriptados)."""
    roles = [assoc.role.name for assoc in orm.roles if assoc.role]
    return User(
        id=orm.id,
        username=orm.username,
        name=orm.name or "",
        surname=orm.surname or "",
        email=decrypt_field(orm.email) if orm.email else "",
        phone=decrypt_field(orm.phone) if orm.phone else "",
        number_id=decrypt_field(orm.number_id) if orm.number_id else "",
        address=orm.address or "",
        status=orm.status if orm.status is not None else 1,
        user_partner=orm.user_partner or "",
        ws_token=orm.ws_token,
        roles=roles,
    )


def domain_to_orm_fields(user: User) -> dict:
    """
    Retorna dict de campos no-PII actualizables.

    Los campos PII (email, phone, number_id) NO se incluyen aquí:
    el repositorio los encripta y los setea explícitamente antes del commit.
    """
    return {
        "username": user.username,
        "name": user.name,
        "surname": user.surname,
        "address": user.address,
        "status": user.status,
        "user_partner": user.user_partner,
    }
