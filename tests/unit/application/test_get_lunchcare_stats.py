"""
Tests unitarios para GetLunchcareStatsUseCase.

REQ: A03 — GetLunchcareStatsUseCase
"""

from datetime import date
from unittest.mock import MagicMock

from app.application.attendance.get_lunchcare_stats import GetLunchcareStatsUseCase
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_use_case(records):
    repo = MagicMock()
    repo.list_by_school_and_date.return_value = records
    return GetLunchcareStatsUseCase(repo)


class TestGetLunchcareStatsWithRecords:
    def test_aggregates_requested(self):
        day = date(2026, 3, 15)
        records = [
            LunchAttendanceFactory.build(lunch_requested=1),
            LunchAttendanceFactory.build(lunch_requested=1),
        ]
        stats = _make_use_case(records).execute(school_id=1, day=day)
        assert stats.total_requested == 2

    def test_aggregates_not_come(self):
        day = date(2026, 3, 15)
        records = [
            LunchAttendanceFactory.build(not_come=1),
            LunchAttendanceFactory.build(not_come=0),
        ]
        stats = _make_use_case(records).execute(school_id=1, day=day)
        assert stats.total_not_come == 1

    def test_aggregates_as_extra(self):
        day = date(2026, 3, 15)
        records = [
            LunchAttendanceFactory.build(as_extra=1),
        ]
        stats = _make_use_case(records).execute(school_id=1, day=day)
        assert stats.total_as_extra == 1


class TestGetLunchcareStatsEmpty:
    def test_returns_zeros_when_no_records(self):
        stats = _make_use_case([]).execute(school_id=1, day=date(2026, 3, 15))
        assert stats.total_requested == 0
        assert stats.total_as_extra == 0
        assert stats.total_not_come == 0
