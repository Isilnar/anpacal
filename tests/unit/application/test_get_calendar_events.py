"""
Tests unitarios para GetCalendarEventsUseCase.

REQ: A01 — GetCalendarEventsUseCase
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.attendance.get_calendar_events import GetCalendarEventsUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_use_case(early_records=None, lunch_records=None):
    early_repo = MagicMock()
    lunch_repo = MagicMock()
    student_repo = MagicMock()
    early_repo.list_by_school_and_date.return_value = early_records or []
    lunch_repo.list_by_school_and_date.return_value = lunch_records or []
    return GetCalendarEventsUseCase(early_repo, lunch_repo, student_repo)


class TestGetCalendarEventsWithRecords:
    def test_returns_merged_events(self):
        day = date(2026, 3, 15)
        early = EarlyAttendanceFactory.build(student_id=10, early_requested=1)
        lunch = LunchAttendanceFactory.build(student_id=10, lunch_requested=1)

        uc = _make_use_case(early_records=[early], lunch_records=[lunch])
        events = uc.execute(school_id=1, day=day)

        assert len(events) == 1
        assert events[0]["student_id"] == 10
        assert events[0]["early"] == early
        assert events[0]["lunch"] == lunch

    def test_student_with_only_early(self):
        day = date(2026, 3, 15)
        early = EarlyAttendanceFactory.build(student_id=20)

        uc = _make_use_case(early_records=[early], lunch_records=[])
        events = uc.execute(school_id=1, day=day)

        assert len(events) == 1
        assert events[0]["student_id"] == 20
        assert events[0]["lunch"] is None

    def test_student_with_only_lunch(self):
        day = date(2026, 3, 15)
        lunch = LunchAttendanceFactory.build(student_id=30)

        uc = _make_use_case(early_records=[], lunch_records=[lunch])
        events = uc.execute(school_id=1, day=day)

        assert len(events) == 1
        assert events[0]["student_id"] == 30
        assert events[0]["early"] is None

    def test_multiple_students_sorted(self):
        day = date(2026, 3, 15)
        early1 = EarlyAttendanceFactory.build(student_id=5)
        early2 = EarlyAttendanceFactory.build(student_id=3)

        uc = _make_use_case(early_records=[early1, early2])
        events = uc.execute(school_id=1, day=day)

        student_ids = [e["student_id"] for e in events]
        assert student_ids == sorted(student_ids)


class TestGetCalendarEventsEmpty:
    def test_returns_empty_list_when_no_records(self):
        day = date(2026, 3, 15)
        uc = _make_use_case()
        events = uc.execute(school_id=1, day=day)
        assert events == []
