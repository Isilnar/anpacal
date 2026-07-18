"""
Tests unitarios para GetEarlycareStatsUseCase.

REQ: A02 — GetEarlycareStatsUseCase
"""

from datetime import date
from unittest.mock import MagicMock

from app.application.attendance.get_earlycare_stats import GetEarlycareStatsUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory


def _make_use_case(records):
    repo = MagicMock()
    repo.list_by_school_and_date.return_value = records
    return GetEarlycareStatsUseCase(repo)


class TestGetEarlycareStatsWithRecords:
    def test_aggregates_requested(self):
        day = date(2026, 3, 15)
        records = [
            EarlyAttendanceFactory.build(early_requested=1, early_plus_requested=0),
            EarlyAttendanceFactory.build(early_requested=1, early_plus_requested=1),
        ]
        stats = _make_use_case(records).execute(school_id=1, day=day)
        assert stats.total_requested == 2
        assert stats.total_plus_requested == 1

    def test_aggregates_not_come(self):
        day = date(2026, 3, 15)
        records = [
            EarlyAttendanceFactory.build(not_come=1),
            EarlyAttendanceFactory.build(not_come=0),
        ]
        stats = _make_use_case(records).execute(school_id=1, day=day)
        assert stats.total_not_come == 1

    def test_aggregates_as_extra(self):
        day = date(2026, 3, 15)
        records = [
            EarlyAttendanceFactory.build(as_extra=1),
            EarlyAttendanceFactory.build(as_extra=1),
        ]
        stats = _make_use_case(records).execute(school_id=1, day=day)
        assert stats.total_as_extra == 2


class TestGetEarlycareStatsEmpty:
    def test_returns_zeros_when_no_records(self):
        stats = _make_use_case([]).execute(school_id=1, day=date(2026, 3, 15))
        assert stats.total_requested == 0
        assert stats.total_plus_requested == 0
        assert stats.total_as_extra == 0
        assert stats.total_not_come == 0
