from __future__ import annotations

from dataclasses import dataclass


@dataclass
class School:
    """Domain entity — sin imports de Flask, SQLAlchemy ni cryptography."""

    name: str
    address: str
    id: int | None = None
    created_at: str | None = None
    phone: str = ""
    email: str = ""
    status: int = 1

    def is_active(self) -> bool:
        return self.status == 1

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "status": self.status,
        }
