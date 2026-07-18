"""
SaveAttendanceRangeUseCase — guarda asistencia para un rango de fechas.

- Filtra feriados usando HolydayRepository.list_active().
- Filtra fines de semana (isoweekday >= 6).
- Upsert por (student_id, date): si existe actualiza, si no crea.
- Un solo commit por operación (el repositorio ya lo hace en save()).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from app.domain.attendance.early_attendance import EarlyAttendance
from app.domain.attendance.lunch_attendance import LunchAttendance
from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)
from app.domain.holyday.repositories import HolydayRepository


@dataclass
class AttendanceItem:
    student_id: int
    early_requested: int = 0
    early_plus_requested: int = 0
    lunch_requested: int = 0
    user_id: int | None = None


@dataclass
class SaveAttendanceRangeDTO:
    school_id: int
    date_from: date
    date_to: date
    attendances: list[AttendanceItem]


@dataclass
class SaveAttendanceRangeResult:
    saved_dates: list[date]
    skipped_dates: list[date]


class SaveAttendanceRangeUseCase:
    """Guarda asistencia en rango, omitiendo feriados y fines de semana."""

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
        holyday_repo: HolydayRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo
        self._holyday = holyday_repo

    def execute(self, dto: SaveAttendanceRangeDTO) -> SaveAttendanceRangeResult:
        if not dto.attendances:
            return SaveAttendanceRangeResult(saved_dates=[], skipped_dates=[])

        # Obtener feriados activos (set de dates para lookup O(1))
        holydays = {h.holyday for h in self._holyday.list_active()}

        saved_dates: list[date] = []
        skipped_dates: list[date] = []

        delta = (dto.date_to - dto.date_from).days
        for i in range(delta + 1):
            day = dto.date_from + timedelta(days=i)

            # Saltar fines de semana
            if day.isoweekday() >= 6:
                skipped_dates.append(day)
                continue

            # Saltar feriados
            if day in holydays:
                skipped_dates.append(day)
                continue

            for item in dto.attendances:
                self._upsert_early(item, day)
                self._upsert_lunch(item, day)

            saved_dates.append(day)

        return SaveAttendanceRangeResult(
            saved_dates=saved_dates,
            skipped_dates=skipped_dates,
        )

    def _upsert_early(self, item: AttendanceItem, day: date) -> None:
        now = datetime.now()
        existing = self._early.find_by_student_and_date(item.student_id, day)
        if existing is not None:
            existing.early_requested = item.early_requested
            existing.early_plus_requested = item.early_plus_requested
            existing.modify_user_id = item.user_id
            existing.modify_date = now
            self._early.save(existing)
        else:
            new = EarlyAttendance(
                student_id=item.student_id,
                early_day=day,
                early_requested=item.early_requested,
                early_plus_requested=item.early_plus_requested,
                user_id=item.user_id,
                modify_user_id=item.user_id,
                modify_date=now,
            )
            self._early.save(new)

    def _upsert_lunch(self, item: AttendanceItem, day: date) -> None:
        now = datetime.now()
        existing = self._lunch.find_by_student_and_date(item.student_id, day)
        if existing is not None:
            existing.lunch_requested = item.lunch_requested
            existing.modify_user_id = item.user_id
            existing.modify_date = now
            self._lunch.save(existing)
        else:
            new = LunchAttendance(
                student_id=item.student_id,
                lunch_day=day,
                lunch_requested=item.lunch_requested,
                user_id=item.user_id,
                modify_user_id=item.user_id,
                modify_date=now,
            )
            self._lunch.save(new)
