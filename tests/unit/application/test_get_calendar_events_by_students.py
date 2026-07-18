"""
Tests unitarios para GetCalendarEventsByStudentsUseCase.

REQ-AC03: GetCalendarEventsByStudentsUseCase encapsula la lógica de get_calendar_events()
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.attendance.get_calendar_events_by_students import GetCalendarEventsByStudentsUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_use_case(early_records=None, lunch_records=None):
    early_repo = MagicMock()
    lunch_repo = MagicMock()
    early_repo.list_by_student_ids_from_date.return_value = early_records or []
    lunch_repo.list_by_student_ids_from_date.return_value = lunch_records or []
    return GetCalendarEventsByStudentsUseCase(early_repo, lunch_repo)


class TestGetCalendarEventsByStudentsEmptyInput:
    def test_returns_empty_list_when_no_student_ids(self):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        uc = GetCalendarEventsByStudentsUseCase(early_repo, lunch_repo)
        result = uc.execute([], date(2026, 5, 1))
        assert result == []
        early_repo.list_by_student_ids_from_date.assert_not_called()
        lunch_repo.list_by_student_ids_from_date.assert_not_called()

    def test_returns_empty_list_when_no_records(self):
        uc = _make_use_case()
        result = uc.execute([1, 2], date(2026, 5, 1))
        assert result == []


class TestGetCalendarEventsByStudentsEarlyOnly:
    def test_early_only_event(self):
        day = date(2026, 5, 10)
        early = EarlyAttendanceFactory.build(student_id=1, early_day=day, early_requested=1, early_plus_requested=0)
        uc = _make_use_case(early_records=[early])
        result = uc.execute([1], date(2026, 5, 1))
        assert len(result) == 1
        assert result[0][1] == "early_only"
        assert result[0][0] == "2026-05-10"
        assert result[0][2] == "20260510"

    def test_early_plus_only_event(self):
        day = date(2026, 5, 12)
        early = EarlyAttendanceFactory.build(student_id=1, early_day=day, early_requested=0, early_plus_requested=1)
        uc = _make_use_case(early_records=[early])
        result = uc.execute([1], date(2026, 5, 1))
        assert len(result) == 1
        assert result[0][1] == "early_plus_only"

    def test_early_not_requested_excluded(self):
        day = date(2026, 5, 10)
        early = EarlyAttendanceFactory.build(student_id=1, early_day=day, early_requested=0, early_plus_requested=0)
        uc = _make_use_case(early_records=[early])
        result = uc.execute([1], date(2026, 5, 1))
        assert result == []


class TestGetCalendarEventsByStudentsLunchOnly:
    def test_lunch_only_event(self):
        day = date(2026, 5, 15)
        lunch = LunchAttendanceFactory.build(student_id=1, lunch_day=day, lunch_requested=1)
        uc = _make_use_case(lunch_records=[lunch])
        result = uc.execute([1], date(2026, 5, 1))
        assert len(result) == 1
        assert result[0][1] == "lunch_only"

    def test_lunch_not_requested_excluded(self):
        day = date(2026, 5, 15)
        lunch = LunchAttendanceFactory.build(student_id=1, lunch_day=day, lunch_requested=0)
        uc = _make_use_case(lunch_records=[lunch])
        result = uc.execute([1], date(2026, 5, 1))
        assert result == []


class TestGetCalendarEventsByStudentsCombined:
    def test_early_lunch_event(self):
        day = date(2026, 5, 20)
        early = EarlyAttendanceFactory.build(student_id=1, early_day=day, early_requested=1, early_plus_requested=0)
        lunch = LunchAttendanceFactory.build(student_id=1, lunch_day=day, lunch_requested=1)
        uc = _make_use_case(early_records=[early], lunch_records=[lunch])
        result = uc.execute([1], date(2026, 5, 1))
        assert len(result) == 1
        assert result[0][1] == "early_lunch"

    def test_early_plus_lunch_event(self):
        day = date(2026, 5, 21)
        early = EarlyAttendanceFactory.build(student_id=1, early_day=day, early_requested=0, early_plus_requested=1)
        lunch = LunchAttendanceFactory.build(student_id=1, lunch_day=day, lunch_requested=1)
        uc = _make_use_case(early_records=[early], lunch_records=[lunch])
        result = uc.execute([1], date(2026, 5, 1))
        assert len(result) == 1
        assert result[0][1] == "early_plus_lunch"

    def test_multiple_days_sorted(self):
        day_a = date(2026, 5, 25)
        day_b = date(2026, 5, 10)
        early_a = EarlyAttendanceFactory.build(student_id=1, early_day=day_a, early_requested=1, early_plus_requested=0)
        early_b = EarlyAttendanceFactory.build(student_id=2, early_day=day_b, early_requested=1, early_plus_requested=0)
        uc = _make_use_case(early_records=[early_a, early_b])
        result = uc.execute([1, 2], date(2026, 5, 1))
        dates = [r[0] for r in result]
        assert dates == sorted(dates)

    def test_repos_called_with_correct_args(self):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        early_repo.list_by_student_ids_from_date.return_value = []
        lunch_repo.list_by_student_ids_from_date.return_value = []
        uc = GetCalendarEventsByStudentsUseCase(early_repo, lunch_repo)
        from_date = date(2026, 5, 1)
        uc.execute([10, 20], from_date)
        early_repo.list_by_student_ids_from_date.assert_called_once_with([10, 20], from_date)
        lunch_repo.list_by_student_ids_from_date.assert_called_once_with([10, 20], from_date)
