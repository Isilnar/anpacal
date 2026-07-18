"""
Tests unitarios para SaveAttendanceRangeUseCase.

REQ: A04 — SaveAttendanceRangeUseCase
"""

from datetime import date
from unittest.mock import MagicMock, call

import pytest

from app.application.attendance.save_attendance_range import (
    AttendanceItem,
    SaveAttendanceRangeDTO,
    SaveAttendanceRangeUseCase,
)
from app.domain.holyday.holyday import Holyday


def _make_use_case(holydays=None):
    early_repo = MagicMock()
    lunch_repo = MagicMock()
    holyday_repo = MagicMock()
    # find_by_student_and_date returns None → siempre crea nuevos
    early_repo.find_by_student_and_date.return_value = None
    lunch_repo.find_by_student_and_date.return_value = None
    # save retorna un mock (no importa el valor en unit tests)
    early_repo.save.return_value = MagicMock()
    lunch_repo.save.return_value = MagicMock()
    holyday_repo.list_active.return_value = holydays or []
    return SaveAttendanceRangeUseCase(early_repo, lunch_repo, holyday_repo)


class TestSaveRangeNoHolydays:
    def test_saves_all_weekdays_in_range(self):
        """Lunes 2026-03-16 a Viernes 2026-03-20 — sin feriados."""
        uc = _make_use_case()
        dto = SaveAttendanceRangeDTO(
            school_id=1,
            date_from=date(2026, 3, 16),
            date_to=date(2026, 3, 20),
            attendances=[AttendanceItem(student_id=1, early_requested=1, lunch_requested=1)],
        )
        result = uc.execute(dto)
        assert len(result.saved_dates) == 5
        assert len(result.skipped_dates) == 0

    def test_skips_weekend_days(self):
        """Viernes a Domingo: solo Viernes se guarda."""
        uc = _make_use_case()
        dto = SaveAttendanceRangeDTO(
            school_id=1,
            date_from=date(2026, 3, 20),  # Viernes
            date_to=date(2026, 3, 22),  # Domingo
            attendances=[AttendanceItem(student_id=1)],
        )
        result = uc.execute(dto)
        assert date(2026, 3, 20) in result.saved_dates
        assert date(2026, 3, 21) in result.skipped_dates  # Sábado
        assert date(2026, 3, 22) in result.skipped_dates  # Domingo


class TestSaveRangeWithHolydays:
    def test_skips_holyday_dates(self):
        """Un feriado en el rango: debe omitirse."""
        holyday = Holyday(holyday=date(2026, 3, 18), status=1)
        uc = _make_use_case(holydays=[holyday])
        dto = SaveAttendanceRangeDTO(
            school_id=1,
            date_from=date(2026, 3, 16),
            date_to=date(2026, 3, 20),
            attendances=[AttendanceItem(student_id=1)],
        )
        result = uc.execute(dto)
        assert date(2026, 3, 18) in result.skipped_dates
        assert date(2026, 3, 18) not in result.saved_dates
        assert len(result.saved_dates) == 4


class TestSaveRangeEmptyAttendances:
    def test_empty_attendances_returns_no_saves(self):
        uc = _make_use_case()
        dto = SaveAttendanceRangeDTO(
            school_id=1,
            date_from=date(2026, 3, 16),
            date_to=date(2026, 3, 20),
            attendances=[],
        )
        result = uc.execute(dto)
        assert result.saved_dates == []
        assert result.skipped_dates == []


class TestSaveRangeUpdatesExisting:
    def test_upsert_early_updates_when_existing(self):
        """_upsert_early: existing != None → actualiza campos y llama save."""
        from tests.factories.early_attendance_factory import EarlyAttendanceFactory

        existing_early = EarlyAttendanceFactory.build(early_requested=0, early_plus_requested=0)
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        holyday_repo = MagicMock()

        early_repo.find_by_student_and_date.return_value = existing_early
        lunch_repo.find_by_student_and_date.return_value = None
        early_repo.save.return_value = MagicMock()
        lunch_repo.save.return_value = MagicMock()
        holyday_repo.list_active.return_value = []

        uc = SaveAttendanceRangeUseCase(early_repo, lunch_repo, holyday_repo)
        dto = SaveAttendanceRangeDTO(
            school_id=1,
            date_from=date(2026, 3, 16),
            date_to=date(2026, 3, 16),
            attendances=[
                AttendanceItem(student_id=existing_early.student_id, early_requested=1, early_plus_requested=0)
            ],
        )
        uc.execute(dto)
        # Must call save on the existing entity (update path)
        early_repo.save.assert_called_once_with(existing_early)
        assert existing_early.early_requested == 1

    def test_upsert_lunch_updates_when_existing(self):
        """_upsert_lunch: existing != None → actualiza lunch_requested y llama save."""
        from tests.factories.lunch_attendance_factory import LunchAttendanceFactory

        existing_lunch = LunchAttendanceFactory.build(lunch_requested=0)
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        holyday_repo = MagicMock()

        early_repo.find_by_student_and_date.return_value = None
        lunch_repo.find_by_student_and_date.return_value = existing_lunch
        early_repo.save.return_value = MagicMock()
        lunch_repo.save.return_value = MagicMock()
        holyday_repo.list_active.return_value = []

        uc = SaveAttendanceRangeUseCase(early_repo, lunch_repo, holyday_repo)
        dto = SaveAttendanceRangeDTO(
            school_id=1,
            date_from=date(2026, 3, 16),
            date_to=date(2026, 3, 16),
            attendances=[AttendanceItem(student_id=existing_lunch.student_id, lunch_requested=1)],
        )
        uc.execute(dto)
        # Must call save on the existing entity (update path)
        lunch_repo.save.assert_called_once_with(existing_lunch)
        assert existing_lunch.lunch_requested == 1
