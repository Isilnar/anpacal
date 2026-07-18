"""
Tests unitarios para EarlyAttendance domain entity.

REQ: D01 — EarlyAttendance Entity
"""

from datetime import date

import pytest

from app.domain.attendance.early_attendance import EarlyAttendance
from tests.factories.early_attendance_factory import EarlyAttendanceFactory


class TestEarlyAttendanceCreation:
    def test_create_valid_early_attendance(self):
        ea = EarlyAttendance(
            student_id=1,
            early_day=date(2026, 3, 15),
            early_requested=1,
            early_plus_requested=0,
        )
        assert ea.student_id == 1
        assert ea.early_day == date(2026, 3, 15)
        assert ea.early_requested == 1
        assert ea.early_plus_requested == 0
        assert ea.status == 1

    def test_create_from_factory(self):
        ea = EarlyAttendanceFactory.build()
        assert ea.student_id is not None
        assert ea.early_requested >= 0
        assert ea.early_plus_requested >= 0

    def test_default_fields(self):
        ea = EarlyAttendance(
            student_id=5,
            early_day=date(2026, 1, 10),
            early_requested=0,
            early_plus_requested=0,
        )
        assert ea.id is None
        assert ea.status == 1
        assert ea.as_extra == 0
        assert ea.not_come == 0
        assert ea.modify_notes == ""


class TestEarlyAttendanceValidation:
    def test_reject_negative_early_requested(self):
        with pytest.raises(ValueError, match="early_requested must be >= 0"):
            EarlyAttendance(
                student_id=1,
                early_day=date(2026, 1, 1),
                early_requested=-1,
                early_plus_requested=0,
            )

    def test_reject_negative_early_plus_requested(self):
        with pytest.raises(ValueError, match="early_plus_requested must be >= 0"):
            EarlyAttendance(
                student_id=1,
                early_day=date(2026, 1, 1),
                early_requested=0,
                early_plus_requested=-1,
            )

    def test_zero_values_are_valid(self):
        ea = EarlyAttendance(
            student_id=1,
            early_day=date(2026, 1, 1),
            early_requested=0,
            early_plus_requested=0,
        )
        assert ea.early_requested == 0
        assert ea.early_plus_requested == 0
