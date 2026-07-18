"""
EarlyAttendanceFactory — Factory Boy para domain entity EarlyAttendance — sin DB.
"""

from datetime import date

import factory

from app.domain.attendance.early_attendance import EarlyAttendance


class EarlyAttendanceFactory(factory.Factory):
    """Factory para EarlyAttendance domain entity — sin DB."""

    class Meta:
        model = EarlyAttendance

    student_id = factory.Sequence(lambda n: n + 1)
    early_day = factory.Sequence(lambda n: date(2026, 1, min(n % 28 + 1, 28)))
    early_requested = 1
    early_plus_requested = 0
    id = factory.Sequence(lambda n: n + 1)
    status = 1
    user_id = None
    as_extra = 0
    not_come = 0
    modify_notes = ""
