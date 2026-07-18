"""
ListSchoolsUseCase — lista schools activos (status=1).
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School


class ListSchoolsUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self) -> list[School]:
        return self.repo.list_active()
