"""
AssignIntolerancesToStudentUseCase — sincroniza las intolerancias asignadas a un alumno.

Delega a StudentRepository.sync_intolerances — sin duplicar lógica.
Transaccional: borra las que ya no están, agrega las nuevas.
"""

from __future__ import annotations

from app.domain.student.repositories import StudentRepository


class AssignIntolerancesToStudentUseCase:
    def __init__(self, student_repo: StudentRepository, student_id: int, intolerance_ids: list[int]):
        self.student_repo = student_repo
        self.student_id = student_id
        self.intolerance_ids = intolerance_ids

    def execute(self) -> None:
        self.student_repo.sync_intolerances(self.student_id, self.intolerance_ids)
