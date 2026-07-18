"""
GetSchoolsByIdsUseCase — obtiene schools filtrados por lista de IDs.
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School


class GetSchoolsByIdsUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self, ids: list[int]) -> list[School]:
        return self.repo.list_by_ids(ids)
