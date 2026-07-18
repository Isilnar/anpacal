"""
DeleteSchoolUseCase — soft-delete de un school (status=0).
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository

from .edit import SchoolNotFoundError


class DeleteSchoolUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self, school_id: int) -> None:
        school = self.repo.get_by_id(school_id)
        if school is None:
            raise SchoolNotFoundError(f"School with id={school_id} not found")

        self.repo.soft_delete(school_id)
