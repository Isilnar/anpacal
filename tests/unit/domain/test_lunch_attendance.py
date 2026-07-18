"""
Tests unitarios para LunchAttendance domain entity.

REQ: D02 — LunchAttendance Entity
"""

from datetime import date

import pytest

from app.domain.attendance.lunch_attendance import LunchAttendance
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


class TestLunchAttendanceCreation:
    def test_create_valid_lunch_attendance(self):
        la = LunchAttendance(
            student_id=2,
            lunch_day=date(2026, 3, 15),
            lunch_requested=1,
        )
        assert la.student_id == 2
        assert la.lunch_day == date(2026, 3, 15)
        assert la.lunch_requested == 1
        assert la.status == 1

    def test_create_from_factory(self):
        la = LunchAttendanceFactory.build()
        assert la.student_id is not None
        assert la.lunch_requested >= 0

    def test_default_fields(self):
        la = LunchAttendance(
            student_id=3,
            lunch_day=date(2026, 1, 10),
            lunch_requested=0,
        )
        assert la.id is None
        assert la.status == 1
        assert la.as_extra == 0
        assert la.not_come == 0
        assert la.modify_notes == ""


class TestLunchAttendanceValidation:
    def test_reject_negative_lunch_requested(self):
        with pytest.raises(ValueError, match="lunch_requested must be >= 0"):
            LunchAttendance(
                student_id=1,
                lunch_day=date(2026, 1, 1),
                lunch_requested=-1,
            )

    def test_zero_is_valid(self):
        la = LunchAttendance(
            student_id=1,
            lunch_day=date(2026, 1, 1),
            lunch_requested=0,
        )
        assert la.lunch_requested == 0
