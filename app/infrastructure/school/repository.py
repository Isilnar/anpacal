"""
SQLAlchemySchoolRepository — implementación de SchoolRepository.

Principios:
- Un solo db.session.commit() por operación de escritura.
- soft_delete() es soft-delete (status=0), nunca borra físicamente.
- Todos los métodos de lectura retornan School (dominio), nunca SchoolORM.
"""

from __future__ import annotations

from app import db
from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School
from app.infrastructure.school.mapper import domain_to_orm_fields, orm_to_domain
from app.infrastructure.school.orm import SchoolORM


class SQLAlchemySchoolRepository(SchoolRepository):
    def get_by_id(self, school_id: int) -> School | None:
        orm = db.session.get(SchoolORM, school_id)
        return orm_to_domain(orm) if orm else None

    def get_by_name_and_address(self, name: str, address: str) -> School | None:
        orm = SchoolORM.query.filter_by(name=name, address=address).first()
        return orm_to_domain(orm) if orm else None

    def list_active(self) -> list[School]:
        orms = SchoolORM.query.filter_by(status=1).all()
        return [orm_to_domain(o) for o in orms]

    def list_all(self) -> list[School]:
        orms = SchoolORM.query.all()
        return [orm_to_domain(o) for o in orms]

    def list_by_ids(self, ids: list[int]) -> list[School]:
        if not ids:
            return []
        orms = SchoolORM.query.filter(SchoolORM.id.in_(ids)).all()
        return [orm_to_domain(o) for o in orms]

    def list_with_selection(self, user_id: int | None) -> list[dict]:
        from app.infrastructure.user.orm import UserSchoolAssociation

        all_orms = SchoolORM.query.filter_by(status=1).all()
        if user_id is not None:
            assocs = UserSchoolAssociation.query.filter_by(user_id=user_id).all()
            selected_ids = {a.school_id for a in assocs}
        else:
            selected_ids = set()
        return [{"id": o.id, "name": o.name, "is_selected": 1 if o.id in selected_ids else 0} for o in all_orms]

    def save(self, school: School) -> School:
        """
        Insert o update:
        - Si school.id es None → nuevo registro.
        - Si school.id tiene valor → update del ORM existente.
        Un solo commit al final.
        """
        if school.id is None:
            orm = SchoolORM()
            db.session.add(orm)
        else:
            orm = db.session.get(SchoolORM, school.id)
            if orm is None:
                raise ValueError(f"School with id={school.id} not found")

        fields = domain_to_orm_fields(school)
        for key, value in fields.items():
            setattr(orm, key, value)

        db.session.commit()
        db.session.refresh(orm)
        return orm_to_domain(orm)

    def soft_delete(self, school_id: int) -> None:
        """Soft-delete: status=0. No elimina físicamente el registro."""
        orm = db.session.get(SchoolORM, school_id)
        if orm is None:
            return
        orm.status = 0
        db.session.commit()
