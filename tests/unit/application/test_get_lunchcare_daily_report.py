"""
Tests para GetLunchcareDailyReportUseCase.

REQ: listado diario de comedor por período — iteración de fechas,
     intolerances string, deduplicación de fechas entre días.
"""

import datetime
from unittest.mock import MagicMock

from app.application.attendance.get_lunchcare_daily_report import GetLunchcareDailyReportUseCase
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory


def _make_use_case(records_by_day=None, student=None, course=None, intolerances_str=""):
    lunch_repo = MagicMock()
    if records_by_day is not None:
        lunch_repo.list_by_day.side_effect = lambda day: records_by_day.get(day, [])
    else:
        lunch_repo.list_by_day.return_value = []

    student_repo = MagicMock()
    student_repo.get_by_id.return_value = student

    course_repo = MagicMock()
    course_repo.get_by_id.return_value = course

    intolerance_repo = MagicMock()
    intolerance_repo.get_string_for_student.return_value = intolerances_str

    return GetLunchcareDailyReportUseCase(lunch_repo, student_repo, course_repo, intolerance_repo)


class TestSingleDaySingleRecord:
    def test_returns_one_entry_for_single_record(self):
        day = datetime.datetime(2026, 3, 15)
        record = LunchAttendanceFactory.build(student_id=1)

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
            intolerances_str="Lactosa",
        )
        result = use_case.execute(day, day)
        assert len(result) == 1
        assert result[0]["lunch_day"] == "2026/03/15"
        assert result[0]["student"] == "García, Ana"
        assert result[0]["course"] == "1º Primaria"
        assert result[0]["intolerances"] == "Lactosa"


class TestNoRecords:
    def test_no_records_returns_empty_list(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert result == []


class TestDateDeduplication:
    def test_two_days_have_separator_row(self):
        day1 = datetime.datetime(2026, 3, 15)
        day2 = datetime.datetime(2026, 3, 16)

        record1 = LunchAttendanceFactory.build(student_id=1)
        record2 = LunchAttendanceFactory.build(student_id=2)

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
        # 2 records + 1 separator = 3 entries
        assert len(result) == 3
        separator = next(r for r in result if r["student"] == "")
        assert separator["lunch_day"] == ""

    def test_same_day_second_record_collapses_date(self):
        day = datetime.datetime(2026, 3, 15)
        record1 = LunchAttendanceFactory.build(student_id=1)
        record2 = LunchAttendanceFactory.build(student_id=2)

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
        dates = [r["lunch_day"] for r in result]
        assert dates[0] == "2026/03/15"
        assert dates[1] == ""


class TestStudentNone:
    def test_student_none_produces_empty_fields(self):
        day = datetime.datetime(2026, 3, 15)
        record = LunchAttendanceFactory.build(student_id=99)

        use_case = _make_use_case(
            records_by_day={day.date(): [record]},
            student=None,
            course=None,
        )
        result = use_case.execute(day, day)
        assert result[0]["student"] == ""
        assert result[0]["course"] == ""
