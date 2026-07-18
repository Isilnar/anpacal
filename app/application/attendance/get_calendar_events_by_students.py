"""
GetCalendarEventsByStudentsUseCase — retorna eventos de calendario para una lista de alumnos.

Encapsula la lógica de get_calendar_events() de utils.py usando repositorios de dominio.
"""

from __future__ import annotations

from datetime import date

from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)


class GetCalendarEventsByStudentsUseCase:
    """
    Retorna lista de eventos de calendario (early + lunch) para student_ids desde from_date.

    Formato de salida: list[tuple[str, str, str]]
        - (date_str: '%Y-%m-%d', event_type: str, date_compact: '%Y%m%d')

    event_type values:
        - 'early_lunch'      — tiene early_requested=1 Y lunch_requested=1
        - 'early_plus_lunch' — tiene early_plus_requested=1 Y lunch_requested=1
        - 'early_only'       — solo early_requested=1
        - 'lunch_only'       — solo lunch_requested=1
        - 'early_plus_only'  — solo early_plus_requested=1
    """

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo

    def execute(self, student_ids: list[int], from_date: date) -> list[tuple]:
        """
        Retorna los eventos de calendario para los alumnos dados desde from_date.

        Args:
            student_ids: lista de IDs de alumnos a consultar
            from_date: fecha de inicio (inclusive) del rango

        Returns:
            Lista ordenada de tuplas (date_str, event_type, date_compact).
        """
        if not student_ids:
            return []

        early_records = self._early.list_by_student_ids_from_date(student_ids, from_date)
        lunch_records = self._lunch.list_by_student_ids_from_date(student_ids, from_date)

        # Construir sets de fechas por tipo (equivalente exacto a la lógica de utils.py)
        lunch_list = {r.lunch_day for r in lunch_records if r.lunch_requested == 1}
        early_list = {r.early_day for r in early_records if r.early_requested == 1}
        early_plus_list = {r.early_day for r in early_records if r.early_plus_requested == 1}

        early_lunch_dates = list(lunch_list.intersection(early_list))
        early_plus_lunch_dates = list(lunch_list.intersection(early_plus_list))
        lunch_dates = list(set(lunch_list.difference(early_list)).difference(early_plus_list))
        early_dates = list(set(early_list.difference(lunch_list)).difference(early_plus_list))
        early_plus_dates = list(set(early_plus_list.difference(lunch_list)).difference(early_list))

        events = []
        events.extend([(d.strftime("%Y-%m-%d"), "early_lunch", d.strftime("%Y%m%d")) for d in early_lunch_dates])
        events.extend(
            [(d.strftime("%Y-%m-%d"), "early_plus_lunch", d.strftime("%Y%m%d")) for d in early_plus_lunch_dates]
        )
        events.extend([(d.strftime("%Y-%m-%d"), "early_only", d.strftime("%Y%m%d")) for d in early_dates])
        events.extend([(d.strftime("%Y-%m-%d"), "lunch_only", d.strftime("%Y%m%d")) for d in lunch_dates])
        events.extend([(d.strftime("%Y-%m-%d"), "early_plus_only", d.strftime("%Y%m%d")) for d in early_plus_dates])
        events.sort()

        return events
