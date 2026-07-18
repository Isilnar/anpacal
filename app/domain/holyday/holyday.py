"""
Holyday — domain entity.

Pure dataclass: no Flask, SQLAlchemy, or cryptography imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Holyday:
    """Domain entity — sin imports de Flask, SQLAlchemy ni cryptography."""

    holyday: date
    id: int | None = None
    status: int = 1
    created_at: datetime | None = None

    def is_active(self) -> bool:
        return self.status == 1

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "holyday": self.holyday,
            "status": self.status,
            "holyday_formated": self.get_formatted_date(),
        }

    def get_formatted_date(self) -> str:
        """Retorna la fecha como dd/mm/yyyy."""
        return self.holyday.strftime("%d/%m/%Y") if self.holyday else ""
