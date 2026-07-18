"""
Tests para GetLunchcareSummaryByDayUseCase.

REQ: resumen diario de comedor — totales + conteo de intolerancias + brothers.
     - Sin registros → total=0, brothers=""
     - brothers counting: brother_number > 1 → counted
"""

import datetime
from unittest.mock import MagicMock

from app.application.attendance.get_lunchcare_summary_by_day import GetLunchcareSummaryByDayUseCase
from app.domain.intolerance.entities import DietIntoleranceEntity
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_intolerance(id: int, description: str) -> DietIntoleranceEntity:
    return DietIntoleranceEntity(id=id, description=description)


def _make_use_case(records_by_day=None, students_by_id=None, intolerances_by_student=None):
    lunch_repo = MagicMock()
    if records_by_day is not None:
        lunch_repo.list_by_day.side_effect = lambda day, non_extra_only=False: records_by_day.get(day, [])
    else:
        lunch_repo.list_by_day.return_value = []

    student_repo = MagicMock()
    if students_by_id is not None:
        student_repo.get_by_id.side_effect = lambda sid: students_by_id.get(sid)
    else:
        student_repo.get_by_id.return_value = None

    intolerance_repo = MagicMock()
    if intolerances_by_student is not None:
        intolerance_repo.get_for_student.side_effect = lambda sid: intolerances_by_student.get(sid, [])
    else:
        intolerance_repo.get_for_student.return_value = []

    return GetLunchcareSummaryByDayUseCase(lunch_repo, student_repo, intolerance_repo)


class TestNoRecords:
    def test_returns_entry_with_zero_total(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert len(result) == 1
        assert result[0]["total"] == 0

    def test_brothers_is_empty_string_when_no_records(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert result[0]["brothers"] == ""

    def test_lunch_day_formatted_correctly(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert result[0]["lunch_day"] == "2026/03/15"


class TestBrotherCounting:
    def test_brother_number_greater_than_1_is_counted(self):
        day = datetime.datetime(2026, 3, 15)
        records = [
            LunchAttendanceFactory.build(student_id=1),
            LunchAttendanceFactory.build(student_id=2),
        ]
        mock_student_with_brothers = MagicMock()
        mock_student_with_brothers.brother_number = 2

        mock_student_no_brothers = MagicMock()
        mock_student_no_brothers.brother_number = 1

        use_case = _make_use_case(
            records_by_day={day.date(): records},
            students_by_id={1: mock_student_with_brothers, 2: mock_student_no_brothers},
        )
        result = use_case.execute(day, day)
        # Only student 1 has brother_number > 1 → brothers = 1
        assert result[0]["brothers"] == 1

    def test_all_students_have_brothers_sums_correctly(self):
        day = datetime.datetime(2026, 3, 15)
        records = [
            LunchAttendanceFactory.build(student_id=1),
            LunchAttendanceFactory.build(student_id=2),
        ]
        mock_student = MagicMock()
        mock_student.brother_number = 3

        use_case = _make_use_case(
            records_by_day={day.date(): records},
            students_by_id={1: mock_student, 2: mock_student},
        )
        result = use_case.execute(day, day)
        assert result[0]["brothers"] == 2

    def test_brother_number_equal_to_1_not_counted(self):
        day = datetime.datetime(2026, 3, 15)
        records = [LunchAttendanceFactory.build(student_id=1)]

        mock_student = MagicMock()
        mock_student.brother_number = 1

        use_case = _make_use_case(
            records_by_day={day.date(): records},
            students_by_id={1: mock_student},
        )
        result = use_case.execute(day, day)
        assert result[0]["brothers"] == ""

    def test_student_none_not_counted(self):
        day = datetime.datetime(2026, 3, 15)
        records = [LunchAttendanceFactory.build(student_id=99)]

        use_case = _make_use_case(
            records_by_day={day.date(): records},
            students_by_id={99: None},
        )
        result = use_case.execute(day, day)
        assert result[0]["brothers"] == ""


class TestIntoleranceCounting:
    def test_intolerance_counts_aggregated_across_students(self):
        day = datetime.datetime(2026, 3, 15)
        records = [
            LunchAttendanceFactory.build(student_id=1),
            LunchAttendanceFactory.build(student_id=2),
        ]
        gluten = _make_intolerance(1, "Gluten")
        lactosa = _make_intolerance(2, "Lactosa")

        mock_student = MagicMock()
        mock_student.brother_number = 0

        use_case = _make_use_case(
            records_by_day={day.date(): records},
            students_by_id={1: mock_student, 2: mock_student},
            intolerances_by_student={1: [gluten], 2: [gluten, lactosa]},
        )
        result = use_case.execute(day, day)
        counts = result[0]["intolerance_counts"]
        assert counts[1][0] == 2  # Gluten for both
        assert counts[2][0] == 1  # Lactosa for one


class TestMultipleDays:
    def test_each_day_generates_one_entry(self):
        day1 = datetime.datetime(2026, 3, 15)
        day2 = datetime.datetime(2026, 3, 16)
        use_case = _make_use_case()
        result = use_case.execute(day1, day2)
        assert len(result) == 2
        assert result[0]["lunch_day"] == "2026/03/15"
        assert result[1]["lunch_day"] == "2026/03/16"
