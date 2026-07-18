from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.school.school import School


class SchoolRepository(ABC):
    """Interfaz de dominio para persistencia de School."""

    @abstractmethod
    def get_by_id(self, school_id: int) -> School | None: ...

    @abstractmethod
    def get_by_name_and_address(self, name: str, address: str) -> School | None: ...

    @abstractmethod
    def list_active(self) -> list[School]: ...

    @abstractmethod
    def list_all(self) -> list[School]: ...

    @abstractmethod
    def list_by_ids(self, ids: list[int]) -> list[School]: ...

    @abstractmethod
    def list_with_selection(self, user_id: int | None) -> list[dict]: ...

    @abstractmethod
    def save(self, school: School) -> School: ...

    @abstractmethod
    def soft_delete(self, school_id: int) -> None: ...
