"""
SchoolCourseEntity — domain entity.

Pure dataclass: no Flask, SQLAlchemy, or cryptography imports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SchoolCourseEntity:
    """Domain entity — sin imports de Flask, SQLAlchemy ni cryptography."""

    id: int | None = None
    description: str | None = None
    status: int = 1
