"""
DeleteStudentUseCase — soft-delete de un estudiante (status=0).
"""

from app.domain.student.repositories import StudentRepository


class StudentNotFoundError(Exception):
    pass


class DeleteStudentUseCase:
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def execute(self, student_id: int) -> None:
        student = self.repo.get_by_id(student_id)
        if student is None:
            raise StudentNotFoundError(f"Student with id={student_id} not found")
        self.repo.soft_delete(student_id)
