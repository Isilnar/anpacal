"""
Mapper: convierte entre StudentORM (SQLAlchemy) y Student (domain dataclass).

Funciones puras — no tienen acceso a DB ni a app context.
La desencriptación de PII la hace el mapper vía decrypt_field.
"""

from app.domain.student.student import Student
from app.infrastructure.crypto import decrypt_field
from app.infrastructure.student.orm import StudentORM


def orm_to_domain(orm: StudentORM) -> Student:
    """Convierte StudentORM → Student dominio (con campos PII desencriptados)."""
    intolerance_ids = [si.intolerance_id for si in (orm.intolerances or [])]
    return Student(
        id=orm.id,
        name=orm.name or "",
        surname=orm.surname or "",
        school_id=int(orm.school_id) if orm.school_id is not None else 0,
        classroom=orm.classroom or "",
        number_id=decrypt_field(orm.number_id) if orm.number_id else "",
        number_id_hash=orm.number_id_hash or "",
        phone=decrypt_field(orm.phone) if orm.phone else "",
        email=decrypt_field(orm.email) if orm.email else "",
        address=decrypt_field(orm.address) if orm.address else "",
        allergies=orm.allergies or "",
        status=orm.status if orm.status is not None else 1,
        childish=orm.childish or "",
        brother_number=orm.brother_number or 0,
        student_number=orm.student_number or "",
        intolerance_ids=intolerance_ids,
    )


def domain_to_orm_fields(student: Student) -> dict:
    """
    Retorna dict de campos no-PII actualizables.

    Los campos PII (number_id, phone, email, address) NO se incluyen aquí:
    el repositorio los encripta y los setea explícitamente antes del commit.
    """
    return {
        "name": student.name,
        "surname": student.surname,
        "school_id": student.school_id,
        "classroom": student.classroom,
        "allergies": student.allergies,
        "status": student.status,
        "childish": student.childish,
        "brother_number": student.brother_number,
        "student_number": student.student_number,
    }
