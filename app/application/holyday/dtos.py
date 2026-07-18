"""DTOs para Holyday use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class HolydayCreateDTO:
    holyday: date

    def __post_init__(self) -> None:
        if not isinstance(self.holyday, date):
            raise ValueError("holyday must be a date")


@dataclass
class HolydayEditDTO:
    holyday_id: int
    holyday: date

    def __post_init__(self) -> None:
        if self.holyday_id <= 0:
            raise ValueError("holyday_id must be a positive integer")
        if not isinstance(self.holyday, date):
            raise ValueError("holyday must be a date")
