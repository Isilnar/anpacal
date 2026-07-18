"""
DietIntoleranceRepository — abstract interface (domain layer).

No SQLAlchemy, Flask, nor cryptography imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.intolerance.entities import DietIntoleranceEntity


class DietIntoleranceRepository(ABC):
    @abstractmethod
    def list_active(self) -> list[DietIntoleranceEntity]:
        """Returns active diet intolerances (status==1) ordered by description ASC."""
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> DietIntoleranceEntity | None:
        """Returns a single DietIntoleranceEntity by id, or None if not found."""
        ...

    @abstractmethod
    def get_for_student(self, student_id: int) -> list[DietIntoleranceEntity]:
        """Returns active diet intolerances assigned to the given student."""
        ...

    def get_string_for_student(self, student_id: int) -> str:
        """Returns descriptions joined by ', ' ordered alphabetically. Empty string when none."""
        entities = self.get_for_student(student_id)
        descriptions = sorted(e.description for e in entities)
        return ", ".join(descriptions)
