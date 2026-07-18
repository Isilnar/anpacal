"""
GetEarlycareStatsUseCase — estadísticas de madrugadores para un colegio y fecha.

Retorna: total solicitados, as_extra, not_come.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.attendance.repositories import EarlyAttendanceRepository


@dataclass
class EarlycareStats:
    total_requested: int = 0
    total_plus_requested: int = 0
    total_as_extra: int = 0
    total_not_come: int = 0


class GetEarlycareStatsUseCase:
    """Agrega estadísticas de early-care para school_id + day."""

    def __init__(self, early_repo: EarlyAttendanceRepository) -> None:
        self._early = early_repo

    def execute(self, school_id: int, day: date) -> EarlycareStats:
        records = self._early.list_by_school_and_date(school_id, day)

        stats = EarlycareStats()
        for r in records:
            stats.total_requested += r.early_requested or 0
            stats.total_plus_requested += r.early_plus_requested or 0
            stats.total_as_extra += r.as_extra or 0
            stats.total_not_come += r.not_come or 0

        return stats
