"""
SearchAttendanceUseCase — búsqueda multi-criterio de registros de asistencia.

Reemplaza la query compuesta en `edit_registers_routes.find_registers_post`.
Produce list[dict] ordenada por key 'date', idéntica al legacy.

register_type values:
    0 → todos (early + early_plus + lunch)
    1 → solo early_requested=1
    2 → solo early_plus_requested=1
    3 → solo lunch_requested=1
"""

from __future__ import annotations

from dataclasses import dataclass
from operator import itemgetter

from app.application.attendance.get_attendance_by_id import (
    _early_to_dict,
    _lunch_to_dict,
)
from app.domain.attendance.repositories import (
    EarlyAttendanceRepository,
    LunchAttendanceRepository,
)
from app.domain.student.repositories import StudentRepository
from app.domain.user.repositories import UserRepository


@dataclass
class SearchAttendanceDTO:
    register_type: int  # 0=all, 1=early, 2=early_plus, 3=lunch
    register_student: int  # 0 → no filter
    register_user: int  # 0 → no filter
    date_from: str  # "YYYY-MM-DD"
    date_until: str  # "YYYY-MM-DD"


class SearchAttendanceUseCase:
    """Búsqueda multi-criterio de asistencia. Devuelve list[dict] ordenada por date."""

    def __init__(
        self,
        early_repo: EarlyAttendanceRepository,
        lunch_repo: LunchAttendanceRepository,
        student_repo: StudentRepository,
        user_repo: UserRepository,
    ) -> None:
        self._early = early_repo
        self._lunch = lunch_repo
        self._students = student_repo
        self._users = user_repo

    def execute(self, dto: SearchAttendanceDTO) -> list[dict]:
        # Resolver student_ids por usuario
        user_student_ids: list[int] = []
        if dto.register_user > 0:
            user_student_ids = self._users.get_student_ids_by_user(dto.register_user)

        student_id = dto.register_student  # 0 → no filter

        list_result: list[dict] = []

        include_early = dto.register_type in (0, 1, 2)
        include_lunch = dto.register_type in (0, 3)

        if include_early:
            early_records = self._early.search(
                student_id=student_id,
                user_student_ids=user_student_ids,
                date_from=dto.date_from,
                date_until=dto.date_until,
            )
            for item in early_records:
                if dto.register_type == 0:
                    if item.early_requested != 1 and item.early_plus_requested != 1:
                        continue
                elif dto.register_type == 1:
                    if item.early_requested != 1:
                        continue
                else:  # type == 2
                    if item.early_plus_requested != 1:
                        continue
                student = self._students.get_by_id(item.student_id)
                fullname = student.get_fullname_reverse() if student else ""
                list_result.append(_early_to_dict(item, fullname))

        if include_lunch:
            lunch_records = self._lunch.search(
                student_id=student_id,
                user_student_ids=user_student_ids,
                date_from=dto.date_from,
                date_until=dto.date_until,
            )
            for item in lunch_records:
                if item.lunch_requested != 1:
                    continue
                student = self._students.get_by_id(item.student_id)
                fullname = student.get_fullname_reverse() if student else ""
                list_result.append(_lunch_to_dict(item, fullname))

        return sorted(list_result, key=itemgetter("date"))
