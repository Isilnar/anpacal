"""
Menu — pure domain dataclass.

Sin imports de Flask, SQLAlchemy ni cryptography.
Singleton lógico: solo 1 registro activo (status=1) a la vez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Menu:
    menu_link: str
    id: int | None = None
    status: int = 1
    created_at: datetime | None = field(default=None)

    def is_active(self) -> bool:
        return self.status == 1

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "menu_link": self.menu_link,
            "status": self.status,
        }
