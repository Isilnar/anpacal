"""
LunchAttendanceFactory — Factory Boy para domain entity LunchAttendance — sin DB.
"""

from datetime import date

import factory

from app.domain.attendance.lunch_attendance import LunchAttendance


class LunchAttendanceFactory(factory.Factory):
    """Factory para LunchAttendance domain entity — sin DB."""

    class Meta:
        model = LunchAttendance

    student_id = factory.Sequence(lambda n: n + 1)
    lunch_day = factory.Sequence(lambda n: date(2026, 1, min(n % 28 + 1, 28)))
    lunch_requested = 1
    id = factory.Sequence(lambda n: n + 1)
    status = 1
    user_id = None
    as_extra = 0
    not_come = 0
    modify_notes = ""
