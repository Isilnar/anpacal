"""
SQLAlchemyStudentRepository — implementación de StudentRepository.

Principios:
- Un solo db.session.commit() por operación de escritura.
- soft_delete() es soft-delete (status=0), nunca borra físicamente.
- save() encripta PII y calcula hashes antes de persistir.
- Todos los métodos de lectura retornan Student (dominio), nunca StudentORM.
"""

from app import db
from app.domain.student.repositories import StudentRepository
from app.domain.student.student import Student
from app.infrastructure.crypto import encrypt_field, hash_field
from app.infrastructure.user.orm import UserStudentAssociation

from .mapper import orm_to_domain
from .orm import StudentIntoleranceORM, StudentORM


class SQLAlchemyStudentRepository(StudentRepository):
    def get_by_id(self, student_id: int) -> Student | None:
        orm = db.session.get(StudentORM, student_id)
        return orm_to_domain(orm) if orm else None

    # Alias para compatibilidad con use cases que usan la convención find_by_id
    def find_by_id(self, student_id: int) -> Student | None:
        return self.get_by_id(student_id)

    def get_by_number_id_hash_and_school(self, nid_hash: str, school_id: int) -> Student | None:
        orm = StudentORM.query.filter_by(number_id_hash=nid_hash, school_id=school_id).first()
        return orm_to_domain(orm) if orm else None

    def list_active(self) -> list[Student]:
        orms = StudentORM.query.filter_by(status=1).all()
        return [orm_to_domain(o) for o in orms]

    def list_active_with_school(self) -> list[Student]:
        """Returns active students (status=1) con school activo (status=1). JOIN real con SchoolORM."""
        from app.infrastructure.school.orm import SchoolORM

        orms = (
            StudentORM.query.join(SchoolORM, StudentORM.school_id == SchoolORM.id)
            .filter(StudentORM.status == 1, SchoolORM.status == 1)
            .all()
        )
        return [orm_to_domain(o) for o in orms]

    def get_associations_for_user(self, user_id: int) -> list[int]:
        """Returns list of student_ids associated to the given user_id."""
        assocs = UserStudentAssociation.query.filter_by(user_id=user_id).all()
        return [a.student_id for a in assocs]

    def save(self, student: Student) -> Student:
        """
        Insert o update:
        - Si student.id es None → nuevo registro.
        - Si student.id tiene valor → update del ORM existente.
        Encripta PII y calcula hashes antes del commit.
        """
        if student.id is None:
            orm = StudentORM()
            db.session.add(orm)
        else:
            orm = db.session.get(StudentORM, student.id)
            if orm is None:
                raise ValueError(f"Student with id={student.id} not found")

        # Campos no-PII
        orm.name = student.name
        orm.surname = student.surname
        orm.school_id = student.school_id
        orm.classroom = student.classroom
        orm.allergies = student.allergies
        orm.status = student.status
        orm.childish = student.childish
        orm.brother_number = student.brother_number
        orm.student_number = student.student_number

        # PII — encriptar + calcular hash para lookup
        if student.number_id:
            orm.number_id = encrypt_field(student.number_id)
            orm.number_id_hash = hash_field(student.number_id)
        if student.phone:
            orm.phone = encrypt_field(student.phone)
        if student.email:
            orm.email = encrypt_field(student.email)
        if student.address:
            orm.address = encrypt_field(student.address)

        db.session.commit()

        # Refrescar para obtener el id generado (caso insert)
        db.session.refresh(orm)
        return orm_to_domain(orm)

    def soft_delete(self, student_id: int) -> None:
        """Soft-delete: status=0. No elimina físicamente el registro."""
        orm = db.session.get(StudentORM, student_id)
        if orm is None:
            return
        orm.status = 0
        db.session.commit()

    def sync_intolerances(self, student_id: int, intolerance_ids: list[int]) -> None:
        """
        Sincroniza las intolerancias del student con la lista proporcionada.
        Elimina las que ya no están, agrega las nuevas — en una sola transacción.
        """
        existing = StudentIntoleranceORM.query.filter_by(student_id=student_id).all()
        existing_ids = {si.intolerance_id for si in existing}
        new_ids = set(intolerance_ids)

        # Eliminar las que ya no están
        for si in existing:
            if si.intolerance_id not in new_ids:
                db.session.delete(si)

        # Agregar las nuevas
        for iid in new_ids:
            if iid not in existing_ids:
                db.session.add(
                    StudentIntoleranceORM(
                        student_id=student_id,
                        intolerance_id=iid,
                    )
                )

        db.session.commit()
