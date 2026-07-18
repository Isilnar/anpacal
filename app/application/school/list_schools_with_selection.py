"""
ListSchoolsWithSelectionUseCase — lista todos los centros marcando cuáles tiene el usuario.
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository


class ListSchoolsWithSelectionUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self, user_id: int | None) -> list[dict]:
        return self.repo.list_with_selection(user_id)
