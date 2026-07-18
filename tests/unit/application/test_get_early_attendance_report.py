"""
Tests para GetEarlyAttendanceReportUseCase.

REQ: informe de asistencia de madrugadores — report_type filtering,
     not_come bool conversion, modify_user_id present/absent,
     student None → empty strings.
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.attendance.get_early_attendance_report import GetEarlyAttendanceReportUseCase
from tests.factories.early_attendance_factory import EarlyAttendanceFactory


def _make_record(**kwargs):
    """Create an EarlyAttendance record with optional overrides."""
    defaults = dict(
        student_id=1,
        early_requested=1,
        early_plus_requested=0,
        not_come=0,
        as_extra=0,
        modify_notes="",
        modify_user_id=None,
        early_day=date(2026, 3, 15),
    )
    defaults.update(kwargs)
    return EarlyAttendanceFactory.build(**defaults)


def _make_use_case(records, student=None, course=None, user=None, is_partner=False):
    early_repo = MagicMock()
    early_repo.list_by_date_range.return_value = records

    student_repo = MagicMock()
    student_repo.get_by_id.return_value = student

    course_repo = MagicMock()
    course_repo.get_by_id.return_value = course

    user_repo = MagicMock()
    user_repo.get_partner_flag.return_value = is_partner
    user_repo.find_by_id.return_value = user

    return GetEarlyAttendanceReportUseCase(early_repo, student_repo, course_repo, user_repo), early_repo


class TestReportTypeFilter:
    def test_report_type_0_passes_none_filter(self):
        use_case, early_repo = _make_use_case(records=[])
        use_case.execute("2026-03-01", "2026-03-31", student_id=0, report_type=0)
        early_repo.list_by_date_range.assert_called_once_with(
            date_from="2026-03-01",
            date_until="2026-03-31",
            student_id=0,
            type_filter=None,
        )

    def test_report_type_1_passes_early_filter(self):
        use_case, early_repo = _make_use_case(records=[])
        use_case.execute("2026-03-01", "2026-03-31", student_id=0, report_type=1)
        early_repo.list_by_date_range.assert_called_once_with(
            date_from="2026-03-01",
            date_until="2026-03-31",
            student_id=0,
            type_filter="early",
        )

    def test_report_type_2_passes_early_plus_filter(self):
        use_case, early_repo = _make_use_case(records=[])
        use_case.execute("2026-03-01", "2026-03-31", student_id=0, report_type=2)
        early_repo.list_by_date_range.assert_called_once_with(
            date_from="2026-03-01",
            date_until="2026-03-31",
            student_id=0,
            type_filter="early_plus",
        )


class TestNotComeConversion:
    def test_not_come_1_becomes_true(self):
        record = _make_record(not_come=1)
        use_case, _ = _make_use_case(records=[record])
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=1, report_type=0)
        assert result[0]["not_come"] is True

    def test_not_come_0_becomes_false(self):
        record = _make_record(not_come=0)
        use_case, _ = _make_use_case(records=[record])
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=1, report_type=0)
        assert result[0]["not_come"] is False


class TestModifyUser:
    def test_modify_user_id_none_no_modified_by_key(self):
        record = _make_record(modify_user_id=None)
        use_case, _ = _make_use_case(records=[record])
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=1, report_type=0)
        assert "modified_by" not in result[0]

    def test_modify_user_id_set_resolves_modified_by(self):
        record = _make_record(modify_user_id=5)
        mock_user = MagicMock()
        mock_user.get_fullname.return_value = "Admin User"
        use_case, _ = _make_use_case(records=[record], user=mock_user)
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=1, report_type=0)
        assert result[0]["modified_by"] == "Admin User"


class TestStudentNone:
    def test_student_none_produces_empty_strings(self):
        record = _make_record()
        use_case, _ = _make_use_case(records=[record], student=None, course=None)
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=1, report_type=0)
        assert result[0]["student"] == ""
        assert result[0]["course"] == ""
        assert result[0]["brother_number"] == ""


class TestStudentPresent:
    def test_student_present_sets_fullname_and_course(self):
        record = _make_record()
        mock_student = MagicMock()
        mock_student.get_fullname_reverse.return_value = "García, Ana"
        mock_student.brother_number = 2
        mock_student.classroom = "1A"

        mock_course = MagicMock()
        mock_course.description = "1º Primaria"

        use_case, _ = _make_use_case(records=[record], student=mock_student, course=mock_course)
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=1, report_type=0)
        assert result[0]["student"] == "García, Ana"
        assert result[0]["course"] == "1º Primaria"
        assert result[0]["brother_number"] == "2"


class TestEmptyResult:
    def test_returns_empty_list_when_no_records(self):
        use_case, _ = _make_use_case(records=[])
        result = use_case.execute("2026-03-01", "2026-03-31", student_id=0, report_type=0)
        assert result == []
