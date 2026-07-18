"""
GetEarlycareDailyReportUseCase — listado diario de madrugadores por período.

Reemplaza la función `earlycare_data()` en reports_routes.py.
Produce la lista de dicts con el mismo formato y deduplicación de fechas.
"""

from __future__ import annotations

import datetime

from app.domain.attendance.repositories import EarlyAttendanceRepository
from app.domain.intolerance.repositories import DietIntoleranceRepository
from app.domain.school_course.repositories import SchoolCourseRepository
from app.domain.student.repositories import StudentRepository


class GetEarlycareDailyReportUseCase:
    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        student_repo: StudentRepository,
        course_repo: SchoolCourseRepository,
        intolerance_repo: DietIntoleranceRepository,
    ) -> None:
        self._early = early_repo
        self._students = student_repo
        self._courses = course_repo
        self._intolerances = intolerance_repo

    def execute(self, first_day: datetime.datetime, last_day: datetime.datetime) -> list[dict]:
        res = []
        current_date = first_day

        while current_date <= last_day:
            day = current_date.date() if hasattr(current_date, "date") else current_date
            regs = self._early.list_by_day(day=day)

            for reg in regs:
                student = self._students.get_by_id(reg.student_id)
                course = self._courses.get_by_id(student.classroom if student else None)
                tmp_intolerances = self._intolerances.get_string_for_student(reg.student_id)

                tmp_data: dict = {
                    "early_day": current_date.strftime("%Y/%m/%d"),
                    "student": student.get_fullname_reverse() if student else "",
                    "course_id": course.id if course else None,
                    "course": course.description if course else "",
                    "intolerances": tmp_intolerances,
                    "notes": "",
                    "early_plus": reg.early_plus_requested == 1,
                }
                res.append(tmp_data)

            current_date = current_date + datetime.timedelta(days=1)

        res = sorted(res, key=lambda d: (d["early_day"], d["course_id"] or 0, d["student"]))

        counter = 0
        tmp_date = ""
        tmp_insert: list[int] = []
        for item in res:
            if counter == 0:
                tmp_date = item["early_day"]
            else:
                if item["early_day"] == tmp_date:
                    item["early_day"] = ""
                else:
                    tmp_insert.append(counter)
                    tmp_date = item["early_day"]
            counter += 1

        empty: dict = {
            "early_day": "",
            "student": "",
            "course": "",
            "intolerances": "",
            "notes": "",
            "early_plus": "",
        }
        tmp_insert.reverse()
        for idx in tmp_insert:
            res.insert(idx, empty)

        return res
