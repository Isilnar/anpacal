"""
GetCalendarEventsUseCase — retorna lista de eventos de asistencia por alumno.

Combina EarlyAttendance y LunchAttendance para una fecha dada en un colegio.
"""

from __future__ import annotations

from datetime import date

from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)
from app.domain.student.repositories import StudentRepository


class GetCalendarEventsUseCase:
    """Retorna eventos de asistencia (early + lunch) por alumno para school_id + date."""

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
        student_repo: StudentRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo
        self._students = student_repo

    def execute(self, school_id: int, day: date) -> list[dict]:
        """
        Retorna lista de dicts: [{student_id, early, lunch}].
        Incluye solo alumnos con al menos un registro de asistencia para ese día.
        """
        early_records = self._early.list_by_school_and_date(school_id, day)
        lunch_records = self._lunch.list_by_school_and_date(school_id, day)

        # Indexar por student_id para merge eficiente
        early_by_student = {e.student_id: e for e in early_records}
        lunch_by_student = {ln.student_id: ln for ln in lunch_records}

        all_student_ids = set(early_by_student) | set(lunch_by_student)

        events = []
        for student_id in sorted(all_student_ids):
            events.append(
                {
                    "student_id": student_id,
                    "early": early_by_student.get(student_id),
                    "lunch": lunch_by_student.get(student_id),
                }
            )

        return events
