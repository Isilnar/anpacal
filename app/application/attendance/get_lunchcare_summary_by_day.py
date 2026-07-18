"""
GetLunchcareSummaryByDayUseCase — resumen diario de comedor (totales + intolerancias).

Reemplaza la función `lunchcare_data()` en reports_routes.py.
Produce la lista de dicts con el mismo formato: total, intolerances, brothers.
"""

from __future__ import annotations

import datetime

from app.domain.attendance.repositories import LunchAttendanceRepository
from app.domain.intolerance.repositories import DietIntoleranceRepository
from app.domain.student.repositories import StudentRepository


class GetLunchcareSummaryByDayUseCase:
    def __init__(
        self,
        lunch_repo: LunchAttendanceRepository,
        student_repo: StudentRepository,
        intolerance_repo: DietIntoleranceRepository,
    ) -> None:
        self._lunch = lunch_repo
        self._students = student_repo
        self._intolerances = intolerance_repo

    def execute(self, first_day: datetime.datetime, last_day: datetime.datetime) -> list[dict]:
        res = []
        current_date = first_day

        while current_date <= last_day:
            day = current_date.date() if hasattr(current_date, "date") else current_date
            # non_extra_only=True replicates: filter(StudentLunch.as_extra.is_(None))
            regs = self._lunch.list_by_day(day=day, non_extra_only=True)

            tmp_total = len(regs)
            tmp_intolerances: dict = {}
            tmp_brothers: int | str = ""

            for reg in regs:
                student = self._students.get_by_id(reg.student_id)
                if student and student.brother_number > 1:
                    if tmp_brothers == "":
                        tmp_brothers = 0
                    tmp_brothers = tmp_brothers + 1

                intols = self._intolerances.get_for_student(reg.student_id)
                for intol in intols:
                    if intol.id in tmp_intolerances:
                        tmp_intolerances[intol.id][0] += 1
                    else:
                        tmp_intolerances[intol.id] = [1, intol.description]

            res.append(
                {
                    "lunch_day": current_date.strftime("%Y/%m/%d"),
                    "total": tmp_total,
                    "intolerance_counts": dict(tmp_intolerances),
                    "notes": "",
                    "brothers": tmp_brothers,
                }
            )

            current_date = current_date + datetime.timedelta(days=1)

        return res
