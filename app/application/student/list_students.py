"""
ListStudentsUseCase — retorna la lista de estudiantes activos (status=1).
"""

from app.domain.student.repositories import StudentRepository
from app.domain.student.student import Student


class ListStudentsUseCase:
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def execute(self) -> list[Student]:
        return self.repo.list_active()
