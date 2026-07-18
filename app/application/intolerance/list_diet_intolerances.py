"""
ListDietIntolerancesUseCase — lista todas las intolerancias activas con flag de selección.

Dado un student_id opcional, marca como selected las que el alumno tiene asignadas.
Output: list[dict] con claves {id, description, selected: bool} ordenado por description.
"""

from __future__ import annotations

from app.domain.intolerance.repositories import DietIntoleranceRepository


class ListDietIntolerancesUseCase:
    def __init__(self, repo: DietIntoleranceRepository, student_id: int | None = None):
        self.repo = repo
        self.student_id = student_id

    def execute(self) -> list[dict]:
        all_active = self.repo.list_active()  # already ordered by description ASC

        assigned_ids: set[int] = set()
        if self.student_id is not None:
            assigned = self.repo.get_for_student(self.student_id)
            assigned_ids = {e.id for e in assigned}

        return [
            {
                "id": e.id,
                "description": e.description,
                "selected": e.id in assigned_ids,
            }
            for e in all_active
        ]
