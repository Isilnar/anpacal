"""
HolydayRepository — abstract interface (domain layer).

No SQLAlchemy, Flask, nor cryptography imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.domain.holyday.holyday import Holyday


class HolydayRepository(ABC):
    @abstractmethod
    def find_by_id(self, holyday_id: int) -> Holyday | None: ...

    @abstractmethod
    def find_by_date(self, d: date) -> Holyday | None: ...

    @abstractmethod
    def list_active(self) -> list[Holyday]:
        """Returns active holydays ordered by holyday ASC."""
        ...

    @abstractmethod
    def save(self, holyday: Holyday) -> Holyday: ...

    @abstractmethod
    def delete(self, holyday_id: int) -> None:
        """Soft-delete: sets status=0."""
        ...
