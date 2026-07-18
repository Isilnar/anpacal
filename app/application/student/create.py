"""
CreateStudentUseCase — crea un nuevo estudiante.

Flujo:
1. Verificar que no exista un estudiante con el mismo number_id_hash en la misma escuela.
2. Construir Student dominio con los datos del DTO.
3. repo.save(student) — el repo encripta PII, calcula hash y persiste en UN solo commit.
4. sync_intolerances si se proporcionaron.
5. Retornar Student creado.
"""

from app.domain.student.repositories import StudentRepository
from app.domain.student.student import Student
from app.domain.user.services import CryptoService

from .dtos import StudentCreateDTO


class DuplicateStudentError(Exception):
    pass


class CreateStudentUseCase:
    def __init__(self, repo: StudentRepository, crypto: CryptoService):
        self.repo = repo
        self.crypto = crypto

    def execute(self, dto: StudentCreateDTO) -> Student:
        # 1. Verificar duplicado por hash de number_id en la misma escuela
        if dto.number_id:
            nid_hash = self.crypto.hash_value(dto.number_id)
            existing = self.repo.get_by_number_id_hash_and_school(nid_hash, dto.school_id)
            if existing is not None:
                raise DuplicateStudentError(f"Student with number_id already exists in school {dto.school_id}")

        # 2. Construir Student dominio (sin id — save lo asignará)
        student = Student(
            name=dto.name,
            surname=dto.surname,
            school_id=dto.school_id,
            classroom=dto.classroom,
            number_id=dto.number_id,
            phone=dto.phone,
            email=dto.email,
            address=dto.address,
            allergies=dto.allergies,
            childish=dto.childish,
            brother_number=dto.brother_number,
            student_number=dto.student_number,
            status=1,
        )

        # 3. Persistir — el repo encripta PII en UN solo commit
        saved = self.repo.save(student)

        # 4. Sync intolerances si se proporcionaron
        if dto.intolerance_ids is not None:
            self.repo.sync_intolerances(saved.id, dto.intolerance_ids)

        return saved
