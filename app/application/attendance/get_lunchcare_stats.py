"""
GetLunchcareStatsUseCase — estadísticas de comedor para un colegio y fecha.

Retorna: total solicitados, as_extra, not_come.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.attendance.repositories import LunchAttendanceRepository


@dataclass
class LunchcareStats:
    total_requested: int = 0
    total_as_extra: int = 0
    total_not_come: int = 0


class GetLunchcareStatsUseCase:
    """Agrega estadísticas de lunch-care para school_id + day."""

    def __init__(self, lunch_repo: LunchAttendanceRepository) -> None:
        self._lunch = lunch_repo

    def execute(self, school_id: int, day: date) -> LunchcareStats:
        records = self._lunch.list_by_school_and_date(school_id, day)

        stats = LunchcareStats()
        for r in records:
            stats.total_requested += r.lunch_requested or 0
            stats.total_as_extra += r.as_extra or 0
            stats.total_not_come += r.not_come or 0

        return stats
