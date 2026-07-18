"""
Tests para GetEarlycareDailyReportUseCase.

REQ: listado diario de madrugadores por período — iteración de fechas,
     early_plus_requested=1 → early_plus=True, intolerances string,
     deduplicación de fechas entre días.
"""

import datetime
from unittest.mock import MagicMock

from app.application.attendance.get_earlycare_daily_report import GetEarlycareDailyReportUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory


def _make_use_case(records_by_day=None, student=None, course=None, intolerances_str=""):
    """
    records_by_day: dict mapping date → list of records.
    If None, all calls return [].
    """
    early_repo = MagicMock()
    if records_by_day is not None:
        early_repo.list_by_day.side_effect = lambda day: records_by_day.get(day, [])
    else:
        early_repo.list_by_day.return_value = []

    student_repo = MagicMock()
    student_repo.get_by_id.return_value = student

    course_repo = MagicMock()
    course_repo.get_by_id.return_value = course

    intolerance_repo = MagicMock()
    intolerance_repo.get_string_for_student.return_value = intolerances_str

    return GetEarlycareDailyReportUseCase(early_repo, student_repo, course_repo, intolerance_repo)


class TestSingleDaySingleRecord:
    def test_returns_one_entry_for_single_record(self):
        day = datetime.datetime(2026, 3, 15)
        record = EarlyAttendanceFactory.build(student_id=1, early_plus_requested=0)

        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "García, Ana"
        mock_student.classroom = "1A"

        mock_course = MagicMock()
        mock_course.id = 10
        mock_course.description = "1º Primaria"

        use_case = _make_use_case(
            records_by_day={day.date(): [record]},
            student=mock_student,
            course=mock_course,
            intolerances_str="Gluten",
        )

        result = use_case.execute(day, day)
        # One record, no deduplication needed
        assert len(result) == 1
        assert result[0]["early_day"] == "2026/03/15"
        assert result[0]["student"] == "García, Ana"
        assert result[0]["course"] == "1º Primaria"
        assert result[0]["intolerances"] == "Gluten"
        assert result[0]["early_plus"] is False

    def test_early_plus_requested_1_sets_true(self):
        day = datetime.datetime(2026, 3, 15)
        record = EarlyAttendanceFactory.build(student_id=1, early_plus_requested=1)

        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "López, Pedro"
        mock_student.classroom = "2B"

        mock_course = MagicMock()
        mock_course.id = 20
        mock_course.description = "2º Primaria"

        use_case = _make_use_case(
            records_by_day={day.date(): [record]},
            student=mock_student,
            course=mock_course,
        )
        result = use_case.execute(day, day)
        assert result[0]["early_plus"] is True


class TestNoRecords:
    def test_no_records_returns_empty_list(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert result == []


class TestDateDeduplication:
    def test_two_days_second_day_gets_separator_row(self):
        day1 = datetime.datetime(2026, 3, 15)
        day2 = datetime.datetime(2026, 3, 16)

        record1 = EarlyAttendanceFactory.build(student_id=1)
        record2 = EarlyAttendanceFactory.build(student_id=2)

        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "Student, Name"
        mock_student.classroom = "1A"

        mock_course = MagicMock()
        mock_course.id = 1
        mock_course.description = "1º"

        use_case = _make_use_case(
            records_by_day={day1.date(): [record1], day2.date(): [record2]},
            student=mock_student,
            course=mock_course,
        )
        result = use_case.execute(day1, day2)
        # Should have 3 entries: day1 record, empty separator, day2 record
        assert len(result) == 3
        # Separator has empty fields
        separator = next(r for r in result if r["student"] == "")
        assert separator["early_day"] == ""
        assert separator["course"] == ""

    def test_same_day_duplicates_collapsed(self):
        day = datetime.datetime(2026, 3, 15)
        record1 = EarlyAttendanceFactory.build(student_id=1)
        record2 = EarlyAttendanceFactory.build(student_id=2)

        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "Student, Name"
        mock_student.classroom = "1A"

        mock_course = MagicMock()
        mock_course.id = 1
        mock_course.description = "1º"

        use_case = _make_use_case(
            records_by_day={day.date(): [record1, record2]},
            student=mock_student,
            course=mock_course,
        )
        result = use_case.execute(day, day)
        # Two records same day — first keeps date, second gets ""
        dates = [r["early_day"] for r in result]
        assert dates[0] == "2026/03/15"
        assert dates[1] == ""


class TestStudentNone:
    def test_student_none_produces_empty_fields(self):
        day = datetime.datetime(2026, 3, 15)
        record = EarlyAttendanceFactory.build(student_id=99)

        use_case = _make_use_case(
            records_by_day={day.date(): [record]},
            student=None,
            course=None,
        )
        result = use_case.execute(day, day)
        assert result[0]["student"] == ""
        assert result[0]["course"] == ""
