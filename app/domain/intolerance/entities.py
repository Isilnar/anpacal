"""
DietIntoleranceEntity — domain entity.

Pure dataclass: no Flask, SQLAlchemy, or cryptography imports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DietIntoleranceEntity:
    """Domain entity — sin imports de Flask, SQLAlchemy ni cryptography."""

    id: int
    description: str
    status: int = 1

    def is_active(self) -> bool:
        return self.status == 1
