"""
GetSchoolCourseUseCase — obtiene un SchoolCourse por id.

Devuelve None si no existe (el adaptador aplica el fallback course.description → "").
"""

from __future__ import annotations

from app.domain.school_course.entities import SchoolCourseEntity
from app.domain.school_course.repositories import SchoolCourseRepository


class GetSchoolCourseUseCase:
    def __init__(self, repo: SchoolCourseRepository, course_id: int):
        self.repo = repo
        self.course_id = course_id

    def execute(self) -> SchoolCourseEntity | None:
        return self.repo.get_by_id(self.course_id)
