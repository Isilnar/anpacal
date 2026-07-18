"""
GetEarlyAttendanceReportUseCase — informe de asistencia de madrugadores.

Reemplaza la función `early_data()` en reports_routes.py.
Produce dicts idénticos a los que generaba esa función.
"""

from __future__ import annotations

from app.domain.attendance.repositories import EarlyAttendanceRepository
from app.domain.school_course.repositories import SchoolCourseRepository
from app.domain.student.repositories import StudentRepository
from app.domain.user.repositories import UserRepository


class GetEarlyAttendanceReportUseCase:
    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        student_repo: StudentRepository,
        course_repo: SchoolCourseRepository,
        user_repo: UserRepository,
    ) -> None:
        self._early = early_repo
        self._students = student_repo
        self._courses = course_repo
        self._users = user_repo

    def execute(
        self,
        date_from: str,
        date_until: str,
        student_id: int,
        report_type: int,
    ) -> list[dict]:
        """
        report_type=0 → ambos (early + early_plus)
        report_type=1 → solo early
        report_type=2 → solo early_plus
        """
        if report_type == 0:
            type_filter = None
        elif report_type == 1:
            type_filter = "early"
        else:
            type_filter = "early_plus"

        records = self._early.list_by_date_range(
            date_from=date_from,
            date_until=date_until,
            student_id=student_id,
            type_filter=type_filter,
        )

        res = []
        for item in records:
            is_partner = self._users.get_partner_flag(item.student_id)
            student = self._students.get_by_id(item.student_id)
            course = self._courses.get_by_id(student.classroom if student else None)

            tmp: dict = {
                "measure_datetime": None,
                "early_day": item.early_day,
                "early_requested": item.early_requested,
                "early_plus_requested": item.early_plus_requested,
                "student_id": item.student_id,
            }
            tmp["course"] = course.description if course else ""
            tmp["partner"] = is_partner
            tmp["modified_notes"] = item.modify_notes
            tmp["brother_number"] = str(student.brother_number) if student else ""
            tmp["student"] = student.get_fullname_reverse() if student else ""
            tmp["not_come"] = item.not_come == 1
            tmp["come_as_extra"] = item.as_extra == 1
            tmp["early_plus"] = item.early_requested != 1

            if item.modify_user_id is not None:
                user = self._users.find_by_id(int(item.modify_user_id))
                tmp["modified_by"] = user.get_fullname() if user else ""

            res.append(tmp)

        return res
