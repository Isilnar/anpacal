"""
ListHolydaysUseCase — lista holydays activos ordenados por fecha ASC.
"""

from __future__ import annotations

from app.domain.holyday.holyday import Holyday
from app.domain.holyday.repositories import HolydayRepository


class ListHolydaysUseCase:
    def __init__(self, repo: HolydayRepository):
        self.repo = repo

    def execute(self) -> list[Holyday]:
        return self.repo.list_active()
