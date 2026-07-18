"""
GetHolydayUseCase — obtiene un holyday por id.
"""

from __future__ import annotations

from app.domain.holyday.holyday import Holyday
from app.domain.holyday.repositories import HolydayRepository


class HolydayNotFoundError(Exception):
    pass


class GetHolydayUseCase:
    def __init__(self, repo: HolydayRepository):
        self.repo = repo

    def execute(self, holyday_id: int) -> Holyday:
        holyday = self.repo.find_by_id(holyday_id)
        if holyday is None:
            raise HolydayNotFoundError(f"Holyday id={holyday_id} not found")
        return holyday
