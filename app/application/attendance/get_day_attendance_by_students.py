"""
GetDayAttendanceByStudentsUseCase — retorna flags de asistencia para un día exacto.

Por cada student_id llama a find_by_student_and_date en ambos repositorios y
devuelve un dict con los flags early/early_plus/lunch para ese día.
"""

from __future__ import annotations

from datetime import date

from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)


class GetDayAttendanceByStudentsUseCase:
    """
    Retorna los flags de asistencia (early, early_plus, lunch) para una lista de
    alumnos en un día concreto.

    Formato de salida: list[dict]
        { "id": int, "early": 0|1, "early_plus": 0|1, "lunch": 0|1 }

    Devuelve lista vacía cuando student_ids=[].
    No referencia ningún modelo ORM ni sesión de base de datos.
    """

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo

    def execute(self, student_ids: list[int], day: date) -> list[dict]:
        """
        Retorna uno dict por student_id con los flags de asistencia del día.

        Args:
            student_ids: lista de IDs de alumnos a consultar.
            day: fecha exacta del día.

        Returns:
            Lista de dicts con keys: id, early, early_plus, lunch.
            Lista vacía cuando student_ids=[].
        """
        if not student_ids:
            return []

        result = []
        for sid in student_ids:
            early = self._early.find_by_student_and_date(sid, day)
            lunch = self._lunch.find_by_student_and_date(sid, day)

            early_flag = 1 if early and early.early_requested == 1 else 0
            early_plus_flag = 1 if early and early.early_plus_requested == 1 else 0
            lunch_flag = 1 if lunch and lunch.lunch_requested == 1 else 0

            result.append(
                {
                    "id": sid,
                    "early": early_flag,
                    "early_plus": early_plus_flag,
                    "lunch": lunch_flag,
                }
            )

        return result
