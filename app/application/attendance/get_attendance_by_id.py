"""
GetAttendanceByIdUseCase — obtiene un registro de asistencia por id y tipo.

Reemplaza las queries directas en `edit_registers_routes.get_register_data_post`.
Produce un dict idéntico al legacy get_dict_to_search() de StudentEarly/StudentLunch.
"""

from __future__ import annotations

from datetime import datetime

from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)
from app.domain.student.repositories import StudentRepository


def _early_to_dict(item, student_fullname: str) -> dict:
    """Convierte EarlyAttendance dominio → dict idéntico al legacy."""
    early_date = f"{item.early_day:%Y/%m/%d}"
    early_date_calendar = f"{item.early_day:%d/%m/%Y}"
    measure_dt = f"{datetime.combine(item.early_day, datetime.min.time()):%Y-%m-%d %H:%M:%S}"

    type_text = ""
    type_id = 0
    type_ = ""
    if item.early_requested == 1:
        type_text = "Madrugadores"
        type_id = 1
        type_ = "early"
    if item.early_plus_requested == 1:
        type_text = "Madrugadores con almorzo"
        type_id = 2
        type_ = "early_plus"

    return {
        "measure_datetime": measure_dt,
        "date": early_date,
        "early_requested": item.early_requested,
        "student_id": item.student_id,
        "id": item.id,
        "type": type_,
        "type_id": type_id,
        "type_text": type_text,
        "student": student_fullname,
        "date_calendar": early_date_calendar,
        "modify_notes": item.modify_notes,
        "not_come": item.not_come,
    }


def _lunch_to_dict(item, student_fullname: str) -> dict:
    """Convierte LunchAttendance dominio → dict idéntico al legacy."""
    lunch_date = f"{item.lunch_day:%Y/%m/%d}"
    lunch_date_calendar = f"{item.lunch_day:%d/%m/%Y}"
    measure_dt = f"{datetime.combine(item.lunch_day, datetime.min.time()):%Y-%m-%d %H:%M:%S}"

    return {
        "measure_datetime": measure_dt,
        "date": lunch_date,
        "lunch_requested": item.lunch_requested,
        "student_id": item.student_id,
        "id": item.id,
        "type": "lunch",
        "type_id": 3,
        "type_text": "Comedor",
        "student": student_fullname,
        "date_calendar": lunch_date_calendar,
        "modify_notes": item.modify_notes,
        "not_come": item.not_come,
    }


class GetAttendanceByIdUseCase:
    """Devuelve el dict de un registro de asistencia por id y tipo.

    attendance_type debe ser: "lunch", "early" o "early_plus".
    Retorna {} si no se encuentra el registro.
    """

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
        student_repo: StudentRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo
        self._students = student_repo

    def execute(self, attendance_id: int, attendance_type: str) -> dict:
        if attendance_type == "lunch":
            item = self._lunch.find_by_id(attendance_id)
            if item is None:
                return {}
            student = self._students.get_by_id(item.student_id)
            fullname = student.get_fullname_reverse() if student else ""
            return _lunch_to_dict(item, fullname)
        else:  # "early" or "early_plus"
            item = self._early.find_by_id(attendance_id)
            if item is None:
                return {}
            student = self._students.get_by_id(item.student_id)
            fullname = student.get_fullname_reverse() if student else ""
            return _early_to_dict(item, fullname)
