"""
GetLunchAttendanceReportUseCase — informe de asistencia de comedor.

Reemplaza la función `lunch_data()` en reports_routes.py.
Produce dicts idénticos a los que generaba esa función.
"""

from __future__ import annotations

from app.domain.attendance.repositories import LunchAttendanceRepository
from app.domain.school_course.repositories import SchoolCourseRepository
from app.domain.student.repositories import StudentRepository
from app.domain.user.repositories import UserRepository


class GetLunchAttendanceReportUseCase:
    def __init__(
        self,
        lunch_repo: LunchAttendanceRepository,
        student_repo: StudentRepository,
        course_repo: SchoolCourseRepository,
        user_repo: UserRepository,
    ) -> None:
        self._lunch = lunch_repo
        self._students = student_repo
        self._courses = course_repo
        self._users = user_repo

    def execute(
        self,
        date_from: str,
        date_until: str,
        student_id: int,
    ) -> list[dict]:
        records = self._lunch.list_by_date_range(
            date_from=date_from,
            date_until=date_until,
            student_id=student_id,
        )

        res = []
        for item in records:
            student = self._students.find_by_id(item.student_id)
            course = self._courses.get_by_id(student.classroom if student else None)

            tmp: dict = {
                "measure_datetime": None,
                "lunch_day": item.lunch_day,
                "lunch_requested": item.lunch_requested,
                "student_id": item.student_id,
            }
            tmp["course"] = course.description if course else ""
            tmp["student"] = student.get_fullname_reverse() if student else ""
            tmp["brother_number"] = str(student.brother_number) if student else ""
            tmp["modified_notes"] = item.modify_notes
            tmp["not_come"] = item.not_come == 1
            tmp["come_as_extra"] = item.as_extra == 1

            if item.modify_user_id is not None:
                user = self._users.find_by_id(int(item.modify_user_id))
                tmp["modified_by"] = user.get_fullname() if user else ""

            is_partner = self._users.get_partner_flag(item.student_id)
            tmp["partner"] = is_partner

            res.append(tmp)

        return res
