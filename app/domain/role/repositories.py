"""
RoleRepository — abstract interface (domain layer).

No SQLAlchemy, Flask, nor cryptography imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.role.entities import RoleEntity


class RoleRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[RoleEntity]:
        """Returns all roles (no status filter — Role has no status column)."""
        ...
