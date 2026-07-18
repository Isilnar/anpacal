"""
Tests para SearchAttendanceUseCase.

Cubre:
- register_type=0 y registro con neither early nor early_plus → skipped (line 78)
- register_type=2 con early_plus_requested!=1 → skipped (lines 83-84)
- lunch_requested!=1 → skipped (line 98)
"""

from unittest.mock import MagicMock

import pytest

from app.application.attendance.search_attendance import SearchAttendanceDTO, SearchAttendanceUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_dto(**kwargs):
    defaults = dict(
        register_type=0,
        register_student=0,
        register_user=0,
        date_from="2026-03-01",
        date_until="2026-03-31",
    )
    defaults.update(kwargs)
    return SearchAttendanceDTO(**defaults)


def _make_use_case(early_records=None, lunch_records=None, students_by_id=None):
    early_repo = MagicMock()
    early_repo.search.return_value = early_records or []

    lunch_repo = MagicMock()
    lunch_repo.search.return_value = lunch_records or []

    student_repo = MagicMock()
    if students_by_id:
        student_repo.get_by_id.side_effect = lambda sid: students_by_id.get(sid)
    else:
        student_repo.get_by_id.return_value = None

    user_repo = MagicMock()
    user_repo.get_student_ids_by_user.return_value = []

    return SearchAttendanceUseCase(early_repo, lunch_repo, student_repo, user_repo)


class TestRegisterType0SkipsEmpty:
    def test_type0_skips_record_with_neither_early_nor_plus(self):
        """register_type=0 → skips when early_requested!=1 AND early_plus_requested!=1."""
        # Record with both 0 — should be skipped
        record = EarlyAttendanceFactory.build(early_requested=0, early_plus_requested=0)
        use_case = _make_use_case(early_records=[record])
        dto = _make_dto(register_type=0)
        result = use_case.execute(dto)
        assert result == []

    def test_type0_includes_record_with_early_requested(self):
        """register_type=0 → includes when early_requested==1."""
        record = EarlyAttendanceFactory.build(student_id=1, early_requested=1, early_plus_requested=0)
        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "Student, Test"
        use_case = _make_use_case(
            early_records=[record],
            students_by_id={1: mock_student},
        )
        dto = _make_dto(register_type=0)
        result = use_case.execute(dto)
        assert len(result) == 1


class TestRegisterType1:
    def test_type1_skips_record_without_early_requested(self):
        """register_type=1 → skips when early_requested!=1."""
        record = EarlyAttendanceFactory.build(early_requested=0)
        use_case = _make_use_case(early_records=[record])
        dto = _make_dto(register_type=1)
        result = use_case.execute(dto)
        assert result == []

    def test_type1_includes_early_requested(self):
        record = EarlyAttendanceFactory.build(student_id=1, early_requested=1)
        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "Perez, Ana"
        use_case = _make_use_case(
            early_records=[record],
            students_by_id={1: mock_student},
        )
        dto = _make_dto(register_type=1)
        result = use_case.execute(dto)
        assert len(result) == 1


class TestRegisterType2:
    def test_type2_skips_record_without_early_plus(self):
        """register_type=2 → skips when early_plus_requested!=1 (lines 83-84)."""
        record = EarlyAttendanceFactory.build(early_plus_requested=0)
        use_case = _make_use_case(early_records=[record])
        dto = _make_dto(register_type=2)
        result = use_case.execute(dto)
        assert result == []

    def test_type2_includes_early_plus_requested(self):
        record = EarlyAttendanceFactory.build(student_id=1, early_plus_requested=1)
        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "García, Luis"
        use_case = _make_use_case(
            early_records=[record],
            students_by_id={1: mock_student},
        )
        dto = _make_dto(register_type=2)
        result = use_case.execute(dto)
        assert len(result) == 1


class TestRegisterType3Lunch:
    def test_type3_skips_lunch_record_with_requested_not_1(self):
        """register_type=3 → skips when lunch_requested!=1 (line 98)."""
        record = LunchAttendanceFactory.build(lunch_requested=0)
        use_case = _make_use_case(lunch_records=[record])
        dto = _make_dto(register_type=3)
        result = use_case.execute(dto)
        assert result == []

    def test_type3_includes_lunch_requested_1(self):
        record = LunchAttendanceFactory.build(student_id=1, lunch_requested=1)
        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "Fernández, María"
        use_case = _make_use_case(
            lunch_records=[record],
            students_by_id={1: mock_student},
        )
        dto = _make_dto(register_type=3)
        result = use_case.execute(dto)
        assert len(result) == 1


class TestRegisterUserFiltering:
    def test_user_filter_gets_student_ids(self):
        """register_user > 0 → calls get_student_ids_by_user."""
        early_repo = MagicMock()
        early_repo.search.return_value = []
        lunch_repo = MagicMock()
        lunch_repo.search.return_value = []
        student_repo = MagicMock()
        user_repo = MagicMock()
        user_repo.get_student_ids_by_user.return_value = [1, 2]

        use_case = SearchAttendanceUseCase(early_repo, lunch_repo, student_repo, user_repo)
        dto = _make_dto(register_user=5)
        use_case.execute(dto)
        user_repo.get_student_ids_by_user.assert_called_once_with(5)


class TestResultSorting:
    def test_results_sorted_by_date(self):
        from datetime import date

        record1 = EarlyAttendanceFactory.build(student_id=1, early_requested=1, early_day=date(2026, 3, 20))
        record2 = EarlyAttendanceFactory.build(student_id=2, early_requested=1, early_day=date(2026, 3, 15))

        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "Name, Test"

        use_case = _make_use_case(
            early_records=[record1, record2],
            students_by_id={1: mock_student, 2: mock_student},
        )
        dto = _make_dto(register_type=1)
        result = use_case.execute(dto)
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)
