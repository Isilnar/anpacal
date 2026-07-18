"""
GetCareCalendarEventUseCase — agrega datos de madrugadores y comedor para un día.

Retorna CareCalendarEventDTO con totales, split infantil/primaria e intolerances
tanto para almuerzo (early_plus_requested==1) como para comedor (lunch_requested).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.attendance.repositories import EarlyAttendanceRepository, LunchAttendanceRepository
from app.domain.intolerance.repositories import DietIntoleranceRepository
from app.domain.student.repositories import StudentRepository


@dataclass
class CareCalendarEventDTO:
    almuerzo_total: int = 0
    almuerzo_infantil: int = 0
    almuerzo_primaria: int = 0
    almuerzo_intolerances: str = ""
    comedor_total: int = 0
    comedor_infantil: int = 0
    comedor_primaria: int = 0
    comedor_intolerances: str = ""


class GetCareCalendarEventUseCase:
    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
        student_repo: StudentRepository,
        intolerance_repo: DietIntoleranceRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo
        self._students = student_repo
        self._intolerances = intolerance_repo

    def execute(self, school_id: int, day: date) -> CareCalendarEventDTO:
        dto = CareCalendarEventDTO()

        # --- Almuerzo (madrugadores con almorzo) ---
        early_records = self._early.list_by_school_and_date(school_id, day)
        almuerzo_records = [r for r in early_records if r.early_plus_requested == 1]
        dto.almuerzo_total = len(almuerzo_records)
        almuerzo_intol: dict[int, list] = {}
        for r in almuerzo_records:
            student = self._students.get_by_id(r.student_id)
            if student and student.childish == "SI":
                dto.almuerzo_infantil += 1
            else:
                dto.almuerzo_primaria += 1
            for intol in self._intolerances.get_for_student(r.student_id):
                if intol.id in almuerzo_intol:
                    almuerzo_intol[intol.id][0] += 1
                else:
                    almuerzo_intol[intol.id] = [1, intol.description.lower()]
        dto.almuerzo_intolerances = _format_intolerances(almuerzo_intol)

        # --- Comedor ---
        lunch_records = self._lunch.list_by_school_and_date(school_id, day)
        dto.comedor_total = len(lunch_records)
        comedor_intol: dict[int, list] = {}
        for r in lunch_records:
            student = self._students.get_by_id(r.student_id)
            if student and student.childish == "SI":
                dto.comedor_infantil += 1
            else:
                dto.comedor_primaria += 1
            for intol in self._intolerances.get_for_student(r.student_id):
                if intol.id in comedor_intol:
                    comedor_intol[intol.id][0] += 1
                else:
                    comedor_intol[intol.id] = [1, intol.description.lower()]
        dto.comedor_intolerances = _format_intolerances(comedor_intol)

        return dto


def _format_intolerances(intol_dict: dict) -> str:
    """Formats {id: [count, description]} into 'N alerxia/s desc, ...' string."""
    parts = [f"{v[0]} alerxia/s {v[1]}" for v in intol_dict.values()]
    return ", ".join(parts)
