"""
GetIntolerancesForStudentUseCase — retorna las intolerancias activas asignadas a un alumno.
"""

from __future__ import annotations

from app.domain.intolerance.entities import DietIntoleranceEntity
from app.domain.intolerance.repositories import DietIntoleranceRepository


class GetIntolerancesForStudentUseCase:
    def __init__(self, repo: DietIntoleranceRepository):
        self.repo = repo

    def execute(self, student_id: int) -> list[DietIntoleranceEntity]:
        return self.repo.get_for_student(student_id)
