"""
RoleEntity — domain entity.

Pure dataclass: no Flask, SQLAlchemy, or cryptography imports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoleEntity:
    """Domain entity — sin imports de Flask, SQLAlchemy ni cryptography."""

    id: int
    name: str
    description: str = ""
