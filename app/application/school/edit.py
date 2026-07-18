"""
EditSchoolUseCase — edita un school existente.
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School

from .dtos import SchoolEditDTO


class SchoolNotFoundError(Exception):
    pass


class EditSchoolUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self, dto: SchoolEditDTO) -> School:
        school = self.repo.get_by_id(dto.school_id)
        if school is None:
            raise SchoolNotFoundError(f"School with id={dto.school_id} not found")

        school.name = dto.name
        school.address = dto.address
        school.phone = dto.phone
        school.email = dto.email

        return self.repo.save(school)
