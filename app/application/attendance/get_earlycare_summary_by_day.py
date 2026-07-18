"""
GetEarlycareSummaryByDayUseCase — resumen diario de madrugadores con almorzo (totales + intolerancias).

Reemplaza la función `lunchcare_early_data()` en reports_routes.py.
Produce la lista de dicts con el mismo formato: total, intolerances, notes.
"""

from __future__ import annotations

import datetime

from app.domain.attendance.repositories import EarlyAttendanceRepository
from app.domain.intolerance.repositories import DietIntoleranceRepository


class GetEarlycareSummaryByDayUseCase:
    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        intolerance_repo: DietIntoleranceRepository,
    ) -> None:
        self._early = early_repo
        self._intolerances = intolerance_repo

    def execute(self, first_day: datetime.datetime, last_day: datetime.datetime) -> list[dict]:
        res = []
        current_date = first_day

        while current_date <= last_day:
            day = current_date.date() if hasattr(current_date, "date") else current_date
            # type_filter='plus_only' replicates: filter_by(early_plus_requested=1, early_day=current_date)
            regs = self._early.list_by_day(day=day, type_filter="plus_only")

            tmp_total = len(regs)
            tmp_intolerances: dict = {}

            for reg in regs:
                intols = self._intolerances.get_for_student(reg.student_id)
                for intol in intols:
                    if intol.id in tmp_intolerances:
                        tmp_intolerances[intol.id][0] += 1
                    else:
                        tmp_intolerances[intol.id] = [1, intol.description]

            res.append(
                {
                    "early_day": current_date.strftime("%Y/%m/%d"),
                    "total": tmp_total,
                    "intolerance_counts": dict(tmp_intolerances),
                    "notes": "",
                }
            )

            current_date = current_date + datetime.timedelta(days=1)

        return res
