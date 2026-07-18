"""
EditStudentUseCase — edita un estudiante existente.

Flujo:
1. Buscar student por id — StudentNotFoundError si no existe.
2. Actualizar campos del dominio.
3. Re-cifrar PII solo si cambió.
4. repo.save(student) — un solo commit.
5. sync_intolerances si se proporcionaron.
6. Retornar Student actualizado.
"""

from app.domain.student.repositories import StudentRepository
from app.domain.user.services import CryptoService

from .dtos import StudentEditDTO


class StudentNotFoundError(Exception):
    pass


class EditStudentUseCase:
    def __init__(self, repo: StudentRepository, crypto: CryptoService):
        self.repo = repo
        self.crypto = crypto

    def execute(self, dto: StudentEditDTO):
        student = self.repo.get_by_id(dto.student_id)
        if student is None:
            raise StudentNotFoundError(f"Student with id={dto.student_id} not found")

        # Update non-PII fields
        student.name = dto.name
        student.surname = dto.surname
        student.school_id = dto.school_id
        student.classroom = dto.classroom
        student.allergies = dto.allergies
        student.childish = dto.childish
        student.brother_number = dto.brother_number
        student.student_number = dto.student_number

        # Update PII fields only if they changed
        if dto.number_id and dto.number_id != student.number_id:
            student.number_id = dto.number_id
        if dto.phone and dto.phone != student.phone:
            student.phone = dto.phone
        if dto.email and dto.email != student.email:
            student.email = dto.email
        if dto.address and dto.address != student.address:
            student.address = dto.address

        saved = self.repo.save(student)

        if dto.intolerance_ids is not None:
            self.repo.sync_intolerances(saved.id, dto.intolerance_ids)

        return saved
