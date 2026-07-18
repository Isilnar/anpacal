"""
GetSchoolUseCase — obtiene un school por id.
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School

from .edit import SchoolNotFoundError


class GetSchoolUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self, school_id: int) -> School:
        school = self.repo.get_by_id(school_id)
        if school is None:
            raise SchoolNotFoundError(f"School with id={school_id} not found")
        return school
