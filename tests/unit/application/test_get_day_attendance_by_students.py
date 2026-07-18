"""
Tests unitarios para GetDayAttendanceByStudentsUseCase.

REQ-CS01: execute(student_ids, day) -> list[dict] con flags early/early_plus/lunch.
"""

from datetime import date
from unittest.mock import MagicMock

from app.application.attendance.get_day_attendance_by_students import GetDayAttendanceByStudentsUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_use_case(early_side_effect=None, lunch_side_effect=None):
    """Crea el use case con repos mockeados.

    early_side_effect / lunch_side_effect: callable o lista de valores para
    side_effect de find_by_student_and_date.  None → retorna None por defecto.
    """
    early_repo = MagicMock()
    lunch_repo = MagicMock()
    if early_side_effect is not None:
        early_repo.find_by_student_and_date.side_effect = early_side_effect
    else:
        early_repo.find_by_student_and_date.return_value = None
    if lunch_side_effect is not None:
        lunch_repo.find_by_student_and_date.side_effect = lunch_side_effect
    else:
        lunch_repo.find_by_student_and_date.return_value = None
    return GetDayAttendanceByStudentsUseCase(early_repo, lunch_repo), early_repo, lunch_repo


class TestGetDayAttendanceEmptyInput:
    def test_empty_student_ids_returns_empty_list(self):
        """REQ-CS01 scenario: empty student list → []"""
        uc, early_repo, lunch_repo = _make_use_case()
        result = uc.execute([], date(2026, 5, 12))
        assert result == []
        early_repo.find_by_student_and_date.assert_not_called()
        lunch_repo.find_by_student_and_date.assert_not_called()


class TestGetDayAttendanceAllPresent:
    def test_all_flags_set_when_records_exist(self):
        """REQ-CS01 scenario: attendance found for all students — flags all 1."""
        day = date(2026, 5, 12)
        student_id = 42

        early_record = EarlyAttendanceFactory.build(
            student_id=student_id, early_day=day, early_requested=1, early_plus_requested=1
        )
        lunch_record = LunchAttendanceFactory.build(student_id=student_id, lunch_day=day, lunch_requested=1)

        uc, _, _ = _make_use_case(
            early_side_effect=lambda sid, d: early_record,
            lunch_side_effect=lambda sid, d: lunch_record,
        )
        result = uc.execute([student_id], day)

        assert len(result) == 1
        assert result[0] == {"id": student_id, "early": 1, "early_plus": 1, "lunch": 1}

    def test_repos_called_with_correct_args(self):
        """Repos reciben los argumentos exactos: (student_id, day)."""
        day = date(2026, 5, 12)
        uc, early_repo, lunch_repo = _make_use_case()
        uc.execute([7, 8], day)
        assert early_repo.find_by_student_and_date.call_count == 2
        assert lunch_repo.find_by_student_and_date.call_count == 2
        early_repo.find_by_student_and_date.assert_any_call(7, day)
        early_repo.find_by_student_and_date.assert_any_call(8, day)
        lunch_repo.find_by_student_and_date.assert_any_call(7, day)
        lunch_repo.find_by_student_and_date.assert_any_call(8, day)


class TestGetDayAttendanceNoRecords:
    def test_all_flags_zero_when_no_records(self):
        """REQ-CS01 scenario: no attendance records → all flags 0."""
        day = date(2026, 5, 12)
        student_id = 10
        uc, _, _ = _make_use_case()  # both repos return None by default
        result = uc.execute([student_id], day)
        assert len(result) == 1
        assert result[0] == {"id": student_id, "early": 0, "early_plus": 0, "lunch": 0}


class TestGetDayAttendancePartialRecords:
    def test_early_present_lunch_absent(self):
        """early=1, early_plus=0, lunch=0 cuando solo hay registro early."""
        day = date(2026, 5, 12)
        student_id = 5
        early_record = EarlyAttendanceFactory.build(
            student_id=student_id, early_day=day, early_requested=1, early_plus_requested=0
        )

        uc, _, _ = _make_use_case(
            early_side_effect=lambda sid, d: early_record,
        )
        result = uc.execute([student_id], day)
        assert result[0] == {"id": student_id, "early": 1, "early_plus": 0, "lunch": 0}

    def test_lunch_present_early_absent(self):
        """early=0, early_plus=0, lunch=1 cuando solo hay registro lunch."""
        day = date(2026, 5, 12)
        student_id = 6
        lunch_record = LunchAttendanceFactory.build(student_id=student_id, lunch_day=day, lunch_requested=1)

        uc, _, _ = _make_use_case(
            lunch_side_effect=lambda sid, d: lunch_record,
        )
        result = uc.execute([student_id], day)
        assert result[0] == {"id": student_id, "early": 0, "early_plus": 0, "lunch": 1}

    def test_mixed_students_one_with_all_one_with_none(self):
        """Dos alumnos: uno con todo, otro sin nada."""
        day = date(2026, 5, 12)
        sid_a, sid_b = 1, 2

        early_record = EarlyAttendanceFactory.build(
            student_id=sid_a, early_day=day, early_requested=1, early_plus_requested=1
        )
        lunch_record = LunchAttendanceFactory.build(student_id=sid_a, lunch_day=day, lunch_requested=1)

        def early_side(sid, d):
            return early_record if sid == sid_a else None

        def lunch_side(sid, d):
            return lunch_record if sid == sid_a else None

        uc, _, _ = _make_use_case(
            early_side_effect=early_side,
            lunch_side_effect=lunch_side,
        )
        result = uc.execute([sid_a, sid_b], day)
        assert len(result) == 2

        result_by_id = {r["id"]: r for r in result}
        assert result_by_id[sid_a] == {"id": sid_a, "early": 1, "early_plus": 1, "lunch": 1}
        assert result_by_id[sid_b] == {"id": sid_b, "early": 0, "early_plus": 0, "lunch": 0}

    def test_early_plus_only_flag(self):
        """early_plus=1 cuando early_plus_requested=1 pero early_requested=0."""
        day = date(2026, 5, 12)
        student_id = 9
        early_record = EarlyAttendanceFactory.build(
            student_id=student_id, early_day=day, early_requested=0, early_plus_requested=1
        )

        uc, _, _ = _make_use_case(
            early_side_effect=lambda sid, d: early_record,
        )
        result = uc.execute([student_id], day)
        assert result[0] == {"id": student_id, "early": 0, "early_plus": 1, "lunch": 0}
