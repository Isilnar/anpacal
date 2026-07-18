"""
Tests para SaveSingleAttendanceUseCase.

Cubre:
- report_type=2 en _create_new (early_plus branch — line 84)
- _fetch_existing con entity None → ValueError (lines 103-107)
- report_type=1, 3 en _create_new
- update path (register_id > 0)
"""

import datetime
from unittest.mock import MagicMock

import pytest

from app.application.attendance.save_single_attendance import (
    SaveSingleAttendanceDTO,
    SaveSingleAttendanceUseCase,
)
from tests.factories.early_attendance_factory import EarlyAttendanceFactory
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_dto(**kwargs):
    defaults = dict(
        register_id=0,
        report_type=1,
        student_id=1,
        register_date=datetime.date(2026, 3, 15),
        register_notes="",
        register_extra=False,
        register_not_come=False,
        current_user_id=1,
    )
    defaults.update(kwargs)
    return SaveSingleAttendanceDTO(**defaults)


def _make_use_case(early_return=None, lunch_return=None):
    early_repo = MagicMock()
    early_repo.find_by_id.return_value = early_return
    early_repo.save.return_value = MagicMock()

    lunch_repo = MagicMock()
    lunch_repo.find_by_id.return_value = lunch_return
    lunch_repo.save.return_value = MagicMock()

    return SaveSingleAttendanceUseCase(early_repo, lunch_repo), early_repo, lunch_repo


class TestCreateNewType1:
    def test_creates_early_requested_entity(self):
        use_case, early_repo, _ = _make_use_case()
        result = use_case.execute(_make_dto(register_id=0, report_type=1))
        assert result == {"success": True}
        early_repo.save.assert_called_once()
        saved = early_repo.save.call_args[0][0]
        assert saved.early_requested == 1
        assert saved.early_plus_requested == 0


class TestCreateNewType2:
    def test_creates_early_plus_entity(self):
        """Line 84 — report_type==2 in _create_new."""
        use_case, early_repo, _ = _make_use_case()
        result = use_case.execute(_make_dto(register_id=0, report_type=2))
        assert result == {"success": True}
        early_repo.save.assert_called_once()
        saved = early_repo.save.call_args[0][0]
        assert saved.early_requested == 0
        assert saved.early_plus_requested == 1


class TestCreateNewType3:
    def test_creates_lunch_entity(self):
        use_case, _, lunch_repo = _make_use_case()
        result = use_case.execute(_make_dto(register_id=0, report_type=3))
        assert result == {"success": True}
        lunch_repo.save.assert_called_once()
        saved = lunch_repo.save.call_args[0][0]
        assert saved.lunch_requested == 1


class TestFetchExistingNotFound:
    def test_fetch_early_not_found_raises_value_error(self):
        """Lines 102-103 — early entity is None → ValueError."""
        use_case, _, _ = _make_use_case(early_return=None)
        with pytest.raises(ValueError, match="EarlyAttendance id=99 not found"):
            use_case.execute(_make_dto(register_id=99, report_type=1))

    def test_fetch_lunch_not_found_raises_value_error(self):
        """Lines 105-107 — lunch entity is None → ValueError."""
        use_case, _, _ = _make_use_case(lunch_return=None)
        with pytest.raises(ValueError, match="LunchAttendance id=88 not found"):
            use_case.execute(_make_dto(register_id=88, report_type=3))


class TestUpdateExistingRecord:
    def test_update_early_sets_fields(self):
        existing = EarlyAttendanceFactory.build()
        use_case, early_repo, _ = _make_use_case(early_return=existing)
        dto = _make_dto(
            register_id=existing.id or 1,
            report_type=1,
            register_notes="Test note",
            register_extra=True,
            register_not_come=True,
            current_user_id=7,
        )
        result = use_case.execute(dto)
        assert result == {"success": True}
        assert existing.modify_notes == "Test note"
        assert existing.as_extra == 1
        assert existing.not_come == 1
        assert existing.modify_user_id == 7
        early_repo.save.assert_called_once_with(existing)

    def test_update_lunch_sets_fields(self):
        existing = LunchAttendanceFactory.build()
        use_case, _, lunch_repo = _make_use_case(lunch_return=existing)
        dto = _make_dto(
            register_id=existing.id or 1,
            report_type=3,
            current_user_id=5,
        )
        use_case.execute(dto)
        assert existing.modify_user_id == 5
        lunch_repo.save.assert_called_once_with(existing)
