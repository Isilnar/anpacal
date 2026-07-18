"""
EditHolydayUseCase — edita la fecha de un holyday existente.
"""

from __future__ import annotations

from app.domain.holyday.holyday import Holyday
from app.domain.holyday.repositories import HolydayRepository

from .dtos import HolydayEditDTO


class HolydayNotFoundError(Exception):
    pass


class EditHolydayUseCase:
    def __init__(self, repo: HolydayRepository):
        self.repo = repo

    def execute(self, dto: HolydayEditDTO) -> Holyday:
        holyday = self.repo.find_by_id(dto.holyday_id)
        if holyday is None:
            raise HolydayNotFoundError(f"Holyday id={dto.holyday_id} not found")

        holyday.holyday = dto.holyday
        return self.repo.save(holyday)
