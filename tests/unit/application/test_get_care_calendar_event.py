"""
Tests unitarios para GetCareCalendarEventUseCase.

REQ-EL01: execute(school_id, day) -> CareCalendarEventDTO con totales,
          split infantil/primaria e intolerances para almuerzo y comedor.
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.attendance.get_care_calendar_event import (
    CareCalendarEventDTO,
    GetCareCalendarEventUseCase,
)
from app.domain.intolerance.entities import DietIntoleranceEntity
from tests.factories.early_attendance_factory import EarlyAttendanceFactory
from tests.factories.lunch_attendance_factory import LunchAttendanceFactory
from tests.factories.student_factory import StudentFactory

DAY = date(2026, 5, 12)
SCHOOL_ID = 1


def _make_use_case():
    """Returns (use_case, early_repo, lunch_repo, student_repo, intol_repo) all mocked."""
    early_repo = MagicMock()
    lunch_repo = MagicMock()
    student_repo = MagicMock()
    intol_repo = MagicMock()

    early_repo.list_by_school_and_date.return_value = []
    lunch_repo.list_by_school_and_date.return_value = []
    student_repo.get_by_id.return_value = None
    intol_repo.get_for_student.return_value = []

    uc = GetCareCalendarEventUseCase(early_repo, lunch_repo, student_repo, intol_repo)
    return uc, early_repo, lunch_repo, student_repo, intol_repo


class TestCareCalendarEventEmpty:
    def test_empty_day_returns_zero_dto(self):
        """REQ-EL01 scenario: no records → all DTO fields zero/empty."""
        uc, _, _, _, _ = _make_use_case()
        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_total == 0
        assert dto.almuerzo_infantil == 0
        assert dto.almuerzo_primaria == 0
        assert dto.almuerzo_intolerances == ""
        assert dto.comedor_total == 0
        assert dto.comedor_infantil == 0
        assert dto.comedor_primaria == 0
        assert dto.comedor_intolerances == ""


class TestCareCalendarEventAlmuerzo:
    def test_early_requested_only_not_counted(self):
        """early_requested=1, early_plus_requested=0 → almuerzo_total==0."""
        uc, early_repo, _, _, _ = _make_use_case()
        record = EarlyAttendanceFactory.build(
            student_id=10,
            early_day=DAY,
            early_requested=1,
            early_plus_requested=0,
        )
        early_repo.list_by_school_and_date.return_value = [record]

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_total == 0
        assert dto.almuerzo_infantil == 0
        assert dto.almuerzo_primaria == 0

    def test_early_plus_counted(self):
        """early_plus_requested=1 → almuerzo_total==1."""
        uc, early_repo, _, student_repo, _ = _make_use_case()
        record = EarlyAttendanceFactory.build(
            student_id=10,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [record]
        student_repo.get_by_id.return_value = StudentFactory.build(id=10, childish="")

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_total == 1

    def test_infantil_split(self):
        """student.childish=='SI' → almuerzo_infantil incremented."""
        uc, early_repo, _, student_repo, _ = _make_use_case()
        record = EarlyAttendanceFactory.build(
            student_id=20,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [record]
        student_repo.get_by_id.return_value = StudentFactory.build(id=20, childish="SI")

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_infantil == 1
        assert dto.almuerzo_primaria == 0

    def test_primaria_split(self):
        """student.childish != 'SI' → almuerzo_primaria incremented."""
        uc, early_repo, _, student_repo, _ = _make_use_case()
        record = EarlyAttendanceFactory.build(
            student_id=21,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [record]
        student_repo.get_by_id.return_value = StudentFactory.build(id=21, childish="")

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_primaria == 1
        assert dto.almuerzo_infantil == 0

    def test_student_none_treated_as_primaria(self):
        """student_repo.get_by_id returns None → primaria, no crash."""
        uc, early_repo, _, student_repo, _ = _make_use_case()
        record = EarlyAttendanceFactory.build(
            student_id=99,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [record]
        student_repo.get_by_id.return_value = None

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_primaria == 1
        assert dto.almuerzo_infantil == 0


class TestCareCalendarEventIntolerances:
    def test_single_intolerance(self):
        """1 student with 1 intolerance → '1 alerxia/s gluten'."""
        uc, early_repo, _, student_repo, intol_repo = _make_use_case()
        record = EarlyAttendanceFactory.build(
            student_id=30,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [record]
        student_repo.get_by_id.return_value = StudentFactory.build(id=30, childish="")
        intol_repo.get_for_student.return_value = [
            DietIntoleranceEntity(id=1, description="Gluten", status=1),
        ]

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_intolerances == "1 alerxia/s gluten"

    def test_two_students_same_intolerance(self):
        """2 students with same intolerance → '2 alerxia/s gluten'."""
        uc, early_repo, _, student_repo, intol_repo = _make_use_case()
        record_a = EarlyAttendanceFactory.build(
            student_id=31,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        record_b = EarlyAttendanceFactory.build(
            student_id=32,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [record_a, record_b]
        student_repo.get_by_id.return_value = StudentFactory.build(childish="")
        intol_repo.get_for_student.return_value = [
            DietIntoleranceEntity(id=1, description="Gluten", status=1),
        ]

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_intolerances == "2 alerxia/s gluten"

    def test_comedor_intolerances_separate_from_almuerzo(self):
        """Comedor intolerances don't bleed into almuerzo and vice versa."""
        uc, early_repo, lunch_repo, student_repo, intol_repo = _make_use_case()

        early_record = EarlyAttendanceFactory.build(
            student_id=40,
            early_day=DAY,
            early_requested=0,
            early_plus_requested=1,
        )
        lunch_record = LunchAttendanceFactory.build(
            student_id=41,
            lunch_day=DAY,
            lunch_requested=1,
        )
        early_repo.list_by_school_and_date.return_value = [early_record]
        lunch_repo.list_by_school_and_date.return_value = [lunch_record]
        student_repo.get_by_id.return_value = StudentFactory.build(childish="")

        def intol_side(student_id):
            if student_id == 40:
                return [DietIntoleranceEntity(id=1, description="Gluten", status=1)]
            if student_id == 41:
                return [DietIntoleranceEntity(id=2, description="Lactosa", status=1)]
            return []

        intol_repo.get_for_student.side_effect = intol_side

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.almuerzo_intolerances == "1 alerxia/s gluten"
        assert dto.comedor_intolerances == "1 alerxia/s lactosa"


class TestCaredorInfantilAndIntolerances:
    def test_comedor_infantil_student_increments_comedor_infantil(self):
        """Lunch student with childish=='SI' → comedor_infantil incremented (line 71)."""
        uc, _, lunch_repo, student_repo, _ = _make_use_case()
        record = LunchAttendanceFactory.build(student_id=50, lunch_day=DAY, lunch_requested=1)
        lunch_repo.list_by_school_and_date.return_value = [record]
        student_repo.get_by_id.return_value = StudentFactory.build(id=50, childish="SI")

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.comedor_infantil == 1
        assert dto.comedor_primaria == 0

    def test_two_lunch_students_same_intolerance_counted_correctly(self):
        """Two lunch students with same intolerance → comedor_intol[id][0] += 1 (line 76)."""
        uc, _, lunch_repo, student_repo, intol_repo = _make_use_case()
        record_a = LunchAttendanceFactory.build(student_id=51, lunch_day=DAY, lunch_requested=1)
        record_b = LunchAttendanceFactory.build(student_id=52, lunch_day=DAY, lunch_requested=1)
        lunch_repo.list_by_school_and_date.return_value = [record_a, record_b]
        student_repo.get_by_id.return_value = StudentFactory.build(childish="")
        intol_repo.get_for_student.return_value = [
            DietIntoleranceEntity(id=3, description="Lactosa", status=1),
        ]

        dto = uc.execute(SCHOOL_ID, DAY)

        assert dto.comedor_intolerances == "2 alerxia/s lactosa"
