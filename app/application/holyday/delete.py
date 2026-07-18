"""
DeleteHolydayUseCase — soft-delete (status=0) de un holyday.
"""

from __future__ import annotations

from app.domain.holyday.repositories import HolydayRepository


class HolydayNotFoundError(Exception):
    pass


class DeleteHolydayUseCase:
    def __init__(self, repo: HolydayRepository):
        self.repo = repo

    def execute(self, holyday_id: int) -> None:
        holyday = self.repo.find_by_id(holyday_id)
        if holyday is None:
            raise HolydayNotFoundError(f"Holyday id={holyday_id} not found")

        holyday.status = 0
        self.repo.save(holyday)
