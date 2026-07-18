"""
Tests unitarios para GetAttendanceByIdUseCase, SearchAttendanceUseCase,
y SaveSingleAttendanceUseCase.

REQ-ER05, REQ-ER06, REQ-ER07
"""

import datetime
from unittest.mock import MagicMock

import pytest

from app.application.attendance.get_attendance_by_id import GetAttendanceByIdUseCase
from app.application.attendance.save_single_attendance import (
    SaveSingleAttendanceDTO,
    SaveSingleAttendanceUseCase,
)
from app.application.attendance.search_attendance import (
    SearchAttendanceDTO,
    SearchAttendanceUseCase,
)
from app.domain.attendance.early_attendance import EarlyAttendance
from app.domain.attendance.lunch_attendance import LunchAttendance
from app.domain.student.student import Student

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_early(id=10, student_id=1, early_requested=1, early_plus_requested=0):
    return EarlyAttendance(
        id=id,
        student_id=student_id,
        early_day=datetime.date(2026, 3, 10),
        early_requested=early_requested,
        early_plus_requested=early_plus_requested,
        status=1,
        modify_notes="nota",
        not_come=0,
    )


def _make_lunch(id=20, student_id=2, lunch_requested=1):
    return LunchAttendance(
        id=id,
        student_id=student_id,
        lunch_day=datetime.date(2026, 3, 11),
        lunch_requested=lunch_requested,
        status=1,
        modify_notes="",
        not_come=0,
    )


def _make_student(id=1, name="Ana", surname="García"):
    return Student(id=id, name=name, surname=surname, school_id=1)


# ---------------------------------------------------------------------------
# GetAttendanceByIdUseCase
# ---------------------------------------------------------------------------


class TestGetAttendanceByIdUseCase:
    def _make_uc(self, early=None, lunch=None, student=None):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        student_repo = MagicMock()
        early_repo.find_by_id.return_value = early
        lunch_repo.find_by_id.return_value = lunch
        student_repo.get_by_id.return_value = student
        return GetAttendanceByIdUseCase(early_repo, lunch_repo, student_repo)

    def test_returns_early_dict_for_type_early(self):
        early = _make_early()
        student = _make_student()
        uc = self._make_uc(early=early, student=student)
        result = uc.execute(attendance_id=10, attendance_type="early")
        assert result["id"] == 10
        assert result["type"] == "early"
        assert result["type_id"] == 1
        assert result["type_text"] == "Madrugadores"
        assert result["student_id"] == 1
        assert result["student"] == "García, Ana"
        assert "date" in result
        assert "date_calendar" in result

    def test_returns_early_plus_dict_for_type_early_plus(self):
        early = _make_early(early_requested=0, early_plus_requested=1)
        student = _make_student()
        uc = self._make_uc(early=early, student=student)
        result = uc.execute(attendance_id=10, attendance_type="early_plus")
        assert result["type"] == "early_plus"
        assert result["type_id"] == 2
        assert result["type_text"] == "Madrugadores con almorzo"

    def test_returns_lunch_dict_for_type_lunch(self):
        lunch = _make_lunch()
        student = _make_student(id=2, name="Pedro", surname="López")
        uc = self._make_uc(lunch=lunch, student=student)
        result = uc.execute(attendance_id=20, attendance_type="lunch")
        assert result["id"] == 20
        assert result["type"] == "lunch"
        assert result["type_id"] == 3
        assert result["type_text"] == "Comedor"
        assert result["student"] == "López, Pedro"

    def test_returns_empty_dict_when_not_found(self):
        uc = self._make_uc(early=None)
        result = uc.execute(attendance_id=99, attendance_type="early")
        assert result == {}

    def test_returns_empty_dict_when_lunch_not_found(self):
        uc = self._make_uc(lunch=None)
        result = uc.execute(attendance_id=99, attendance_type="lunch")
        assert result == {}


# ---------------------------------------------------------------------------
# SearchAttendanceUseCase
# ---------------------------------------------------------------------------


class TestSearchAttendanceUseCase:
    def _make_uc(self, early_records=None, lunch_records=None, user_student_ids=None, student=None):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        student_repo = MagicMock()
        user_repo = MagicMock()

        early_repo.search.return_value = early_records or []
        lunch_repo.search.return_value = lunch_records or []
        user_repo.get_student_ids_by_user.return_value = user_student_ids or []
        student_repo.get_by_id.return_value = student or _make_student()

        return SearchAttendanceUseCase(early_repo, lunch_repo, student_repo, user_repo)

    def test_type_all_returns_early_and_lunch(self):
        early = [_make_early()]
        lunch = [_make_lunch()]
        uc = self._make_uc(early_records=early, lunch_records=lunch)
        dto = SearchAttendanceDTO(
            register_type=0,
            register_student=0,
            register_user=0,
            date_from="2026-03-01",
            date_until="2026-03-31",
        )
        result = uc.execute(dto)
        types = [r["type"] for r in result]
        assert "early" in types
        assert "lunch" in types

    def test_type_1_returns_only_early(self):
        early = [_make_early()]
        lunch = [_make_lunch()]
        uc = self._make_uc(early_records=early, lunch_records=lunch)
        dto = SearchAttendanceDTO(
            register_type=1,
            register_student=0,
            register_user=0,
            date_from="2026-03-01",
            date_until="2026-03-31",
        )
        result = uc.execute(dto)
        assert all(r["type"] == "early" for r in result)
        assert len(result) == 1

    def test_type_3_returns_only_lunch(self):
        early = [_make_early()]
        lunch = [_make_lunch()]
        uc = self._make_uc(early_records=early, lunch_records=lunch)
        dto = SearchAttendanceDTO(
            register_type=3,
            register_student=0,
            register_user=0,
            date_from="2026-03-01",
            date_until="2026-03-31",
        )
        result = uc.execute(dto)
        assert all(r["type"] == "lunch" for r in result)
        assert len(result) == 1

    def test_early_with_requested_0_is_excluded_on_type_1(self):
        """early_requested=0 records must be filtered when register_type=1."""
        early = [_make_early(early_requested=0, early_plus_requested=1)]
        uc = self._make_uc(early_records=early)
        dto = SearchAttendanceDTO(
            register_type=1,
            register_student=0,
            register_user=0,
            date_from="2026-03-01",
            date_until="2026-03-31",
        )
        result = uc.execute(dto)
        assert result == []

    def test_result_is_sorted_by_date(self):
        """Results must be sorted by date key ascending."""
        early1 = EarlyAttendance(
            id=1,
            student_id=1,
            early_day=datetime.date(2026, 3, 15),
            early_requested=1,
            early_plus_requested=0,
        )
        early2 = EarlyAttendance(
            id=2,
            student_id=2,
            early_day=datetime.date(2026, 3, 10),
            early_requested=1,
            early_plus_requested=0,
        )
        uc = self._make_uc(early_records=[early1, early2])
        dto = SearchAttendanceDTO(
            register_type=1,
            register_student=0,
            register_user=0,
            date_from="2026-03-01",
            date_until="2026-03-31",
        )
        result = uc.execute(dto)
        assert len(result) == 2
        assert result[0]["date"] < result[1]["date"]

    def test_resolves_student_ids_by_user(self):
        """When register_user > 0, it calls get_student_ids_by_user."""
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        student_repo = MagicMock()
        user_repo = MagicMock()
        early_repo.search.return_value = []
        lunch_repo.search.return_value = []
        user_repo.get_student_ids_by_user.return_value = [5, 6]
        student_repo.get_by_id.return_value = _make_student()

        uc = SearchAttendanceUseCase(early_repo, lunch_repo, student_repo, user_repo)
        dto = SearchAttendanceDTO(
            register_type=0,
            register_student=0,
            register_user=7,
            date_from="2026-03-01",
            date_until="2026-03-31",
        )
        uc.execute(dto)
        user_repo.get_student_ids_by_user.assert_called_once_with(7)
        early_repo.search.assert_called_once_with(
            student_id=0,
            user_student_ids=[5, 6],
            date_from="2026-03-01",
            date_until="2026-03-31",
        )


# ---------------------------------------------------------------------------
# SaveSingleAttendanceUseCase
# ---------------------------------------------------------------------------


class TestSaveSingleAttendanceUseCase:
    def _make_uc(self, early_entity=None, lunch_entity=None):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        if early_entity:
            early_repo.find_by_id.return_value = early_entity
        if lunch_entity:
            lunch_repo.find_by_id.return_value = lunch_entity
        early_repo.save.side_effect = lambda e: e
        lunch_repo.save.side_effect = lambda e: e
        return SaveSingleAttendanceUseCase(early_repo, lunch_repo)

    def test_create_early_returns_success(self):
        uc = self._make_uc()
        dto = SaveSingleAttendanceDTO(
            register_id=0,
            report_type=1,
            student_id=1,
            register_date=datetime.date(2026, 3, 10),
            register_notes="",
            register_extra=False,
            register_not_come=False,
            current_user_id=99,
        )
        result = uc.execute(dto)
        assert result == {"success": True}

    def test_create_early_calls_early_repo_save(self):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        early_repo.save.side_effect = lambda e: e
        uc = SaveSingleAttendanceUseCase(early_repo, lunch_repo)
        dto = SaveSingleAttendanceDTO(
            register_id=0,
            report_type=1,
            student_id=1,
            register_date=datetime.date(2026, 3, 10),
            register_notes="",
            register_extra=False,
            register_not_come=False,
            current_user_id=5,
        )
        uc.execute(dto)
        early_repo.save.assert_called_once()
        lunch_repo.save.assert_not_called()

    def test_create_lunch_calls_lunch_repo_save(self):
        early_repo = MagicMock()
        lunch_repo = MagicMock()
        lunch_repo.save.side_effect = lambda e: e
        uc = SaveSingleAttendanceUseCase(early_repo, lunch_repo)
        dto = SaveSingleAttendanceDTO(
            register_id=0,
            report_type=3,
            student_id=2,
            register_date=datetime.date(2026, 3, 11),
            register_notes="",
            register_extra=False,
            register_not_come=False,
            current_user_id=5,
        )
        uc.execute(dto)
        lunch_repo.save.assert_called_once()
        early_repo.save.assert_not_called()

    def test_update_early_fetches_existing_and_saves(self):
        existing = _make_early(id=42)
        uc = self._make_uc(early_entity=existing)
        dto = SaveSingleAttendanceDTO(
            register_id=42,
            report_type=1,
            student_id=1,
            register_date=datetime.date(2026, 3, 10),
            register_notes="updated note",
            register_extra=False,
            register_not_come=False,
            current_user_id=7,
        )
        result = uc.execute(dto)
        assert result == {"success": True}
        assert existing.modify_notes == "updated note"
        assert existing.modify_user_id == 7

    def test_apply_notes_and_extra_flags(self):
        existing = _make_early(id=55)
        uc = self._make_uc(early_entity=existing)
        dto = SaveSingleAttendanceDTO(
            register_id=55,
            report_type=1,
            student_id=1,
            register_date=datetime.date(2026, 3, 10),
            register_notes="nota nueva",
            register_extra=True,
            register_not_come=True,
            current_user_id=3,
        )
        uc.execute(dto)
        assert existing.modify_notes == "nota nueva"
        assert existing.as_extra == 1
        assert existing.not_come == 1
