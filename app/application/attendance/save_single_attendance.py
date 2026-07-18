"""
SaveSingleAttendanceUseCase — crea o actualiza un registro individual de asistencia.

Reemplaza la lógica en `edit_registers_routes.save_registers_post`.

- register_id == 0 → crear nuevo registro.
- register_id > 0  → actualizar registro existente (fetch por id).

report_type values:
    1 → early_requested=1
    2 → early_plus_requested=1
    3 → lunch_requested=1
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from app.domain.attendance.early_attendance import EarlyAttendance
from app.domain.attendance.lunch_attendance import LunchAttendance
from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)


@dataclass
class SaveSingleAttendanceDTO:
    register_id: int
    report_type: int  # 1=early, 2=early_plus, 3=lunch
    student_id: int
    register_date: datetime.date
    register_notes: str
    register_extra: bool
    register_not_come: bool
    current_user_id: int


class SaveSingleAttendanceUseCase:
    """Crea o actualiza un registro individual de asistencia."""

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo

    def execute(self, dto: SaveSingleAttendanceDTO) -> dict:
        if dto.register_id == 0:
            entity = self._create_new(dto)
        else:
            entity = self._fetch_existing(dto)

        # Aplicar cambios comunes
        entity.modify_user_id = dto.current_user_id
        entity.modify_date = datetime.datetime.now()
        if dto.register_notes:
            entity.modify_notes = dto.register_notes
        if dto.register_extra:
            entity.as_extra = 1
        if dto.register_not_come:
            entity.not_come = 1

        if dto.report_type in (1, 2):
            self._early.save(entity)
        else:
            self._lunch.save(entity)

        return {"success": True}

    def _create_new(self, dto: SaveSingleAttendanceDTO):
        if dto.report_type == 1:
            return EarlyAttendance(
                student_id=dto.student_id,
                early_day=dto.register_date,
                early_requested=1,
                early_plus_requested=0,
                user_id=dto.current_user_id,
            )
        elif dto.report_type == 2:
            return EarlyAttendance(
                student_id=dto.student_id,
                early_day=dto.register_date,
                early_requested=0,
                early_plus_requested=1,
                user_id=dto.current_user_id,
            )
        else:  # type == 3, lunch
            return LunchAttendance(
                student_id=dto.student_id,
                lunch_day=dto.register_date,
                lunch_requested=1,
                user_id=dto.current_user_id,
            )

    def _fetch_existing(self, dto: SaveSingleAttendanceDTO):
        if dto.report_type in (1, 2):
            entity = self._early.find_by_id(dto.register_id)
            if entity is None:
                raise ValueError(f"EarlyAttendance id={dto.register_id} not found")
        else:
            entity = self._lunch.find_by_id(dto.register_id)
            if entity is None:
                raise ValueError(f"LunchAttendance id={dto.register_id} not found")
        return entity
