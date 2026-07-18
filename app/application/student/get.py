"""
GetStudentUseCase — obtiene un estudiante por id con PII desencriptada.

El mapper ya desencripta al convertir ORM → domain, así que el use case
simplemente delega al repositorio.
"""

from app.domain.student.repositories import StudentRepository
from app.domain.student.student import Student


class StudentNotFoundError(Exception):
    pass


class GetStudentUseCase:
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def execute(self, student_id: int) -> Student:
        student = self.repo.get_by_id(student_id)
        if student is None:
            raise StudentNotFoundError(f"Student with id={student_id} not found")
        return student
