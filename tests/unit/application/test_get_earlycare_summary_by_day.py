"""
Tests para GetEarlycareSummaryByDayUseCase.

REQ: resumen diario de madrugadores con almorzo — totales + conteo de intolerancias.
     - Sin registros → total=0, intolerance_counts={}
     - Con registros → totales y counts agregados correctamente
"""

import datetime
from unittest.mock import MagicMock

from app.application.attendance.get_earlycare_summary_by_day import GetEarlycareSummaryByDayUseCase
from app.domain.intolerance.entities import DietIntoleranceEntity
from tests.factories.early_attendance_factory import EarlyAttendanceFactory


def _make_intolerance(id: int, description: str) -> DietIntoleranceEntity:
    return DietIntoleranceEntity(id=id, description=description)


def _make_use_case(records_by_day=None, intolerances_by_student=None):
    early_repo = MagicMock()
    if records_by_day is not None:
        early_repo.list_by_day.side_effect = lambda day, type_filter=None: records_by_day.get(day, [])
    else:
        early_repo.list_by_day.return_value = []

    intolerance_repo = MagicMock()
    if intolerances_by_student is not None:
        intolerance_repo.get_for_student.side_effect = lambda sid: intolerances_by_student.get(sid, [])
    else:
        intolerance_repo.get_for_student.return_value = []

    return GetEarlycareSummaryByDayUseCase(early_repo, intolerance_repo)


class TestNoRecords:
    def test_returns_entry_with_zero_total(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert len(result) == 1
        assert result[0]["total"] == 0
        assert result[0]["intolerance_counts"] == {}

    def test_early_day_formatted_correctly(self):
        day = datetime.datetime(2026, 3, 15)
        use_case = _make_use_case()
        result = use_case.execute(day, day)
        assert result[0]["early_day"] == "2026/03/15"


class TestWithRecords:
    def test_total_equals_number_of_records(self):
        day = datetime.datetime(2026, 3, 15)
        records = [
            EarlyAttendanceFactory.build(student_id=1),
            EarlyAttendanceFactory.build(student_id=2),
        ]
        use_case = _make_use_case(records_by_day={day.date(): records})
        result = use_case.execute(day, day)
        assert result[0]["total"] == 2

    def test_intolerance_counts_aggregated(self):
        day = datetime.datetime(2026, 3, 15)
        records = [
            EarlyAttendanceFactory.build(student_id=1),
            EarlyAttendanceFactory.build(student_id=2),
        ]
        gluten = _make_intolerance(1, "Gluten")
        lactosa = _make_intolerance(2, "Lactosa")

        intolerances_by_student = {
            1: [gluten],
            2: [gluten, lactosa],
        }
        use_case = _make_use_case(
            records_by_day={day.date(): records},
            intolerances_by_student=intolerances_by_student,
        )
        result = use_case.execute(day, day)
        counts = result[0]["intolerance_counts"]
        # Gluten appears for both students → count 2
        assert counts[1][0] == 2
        assert counts[1][1] == "Gluten"
        # Lactosa appears for student 2 only → count 1
        assert counts[2][0] == 1
        assert counts[2][1] == "Lactosa"

    def test_no_intolerances_produces_empty_dict(self):
        day = datetime.datetime(2026, 3, 15)
        records = [EarlyAttendanceFactory.build(student_id=1)]
        use_case = _make_use_case(
            records_by_day={day.date(): records},
            intolerances_by_student={1: []},
        )
        result = use_case.execute(day, day)
        assert result[0]["intolerance_counts"] == {}


class TestMultipleDays:
    def test_each_day_generates_one_entry(self):
        day1 = datetime.datetime(2026, 3, 15)
        day2 = datetime.datetime(2026, 3, 16)
        use_case = _make_use_case()
        result = use_case.execute(day1, day2)
        assert len(result) == 2
        assert result[0]["early_day"] == "2026/03/15"
        assert result[1]["early_day"] == "2026/03/16"
