"""
SchoolCourseRepository — abstract interface (domain layer).

No SQLAlchemy, Flask, nor cryptography imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.school_course.entities import SchoolCourseEntity


class SchoolCourseRepository(ABC):
    @abstractmethod
    def get_by_id(self, course_id: int) -> SchoolCourseEntity | None: ...

    @abstractmethod
    def list_all(self) -> list[SchoolCourseEntity]: ...
