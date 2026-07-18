"""
Tests unitarios para los mappers de attendance.

REQ: Unit/infra — early_orm_to_domain, lunch_orm_to_domain — puras, sin DB.
"""

from datetime import date, datetime
from unittest.mock import MagicMock

from app.infrastructure.attendance.mapper import early_orm_to_domain, lunch_orm_to_domain


def _make_early_orm(**kwargs):
    orm = MagicMock()
    orm.id = kwargs.get("id", 1)
    orm.student_id = kwargs.get("student_id", 1)
    orm.early_day = kwargs.get("early_day", datetime(2026, 3, 15))
    orm.early_requested = kwargs.get("early_requested", 1)
    orm.early_plus_requested = kwargs.get("early_plus_requested", 0)
    orm.status = kwargs.get("status", 1)
    orm.user_id = kwargs.get("user_id", None)
    orm.as_extra = kwargs.get("as_extra", 0)
    orm.not_come = kwargs.get("not_come", 0)
    orm.modify_user_id = kwargs.get("modify_user_id", None)
    orm.modify_date = kwargs.get("modify_date", None)
    orm.modify_notes = kwargs.get("modify_notes", "")
    return orm


def _make_lunch_orm(**kwargs):
    orm = MagicMock()
    orm.id = kwargs.get("id", 1)
    orm.student_id = kwargs.get("student_id", 1)
    orm.lunch_day = kwargs.get("lunch_day", datetime(2026, 3, 15))
    orm.lunch_requested = kwargs.get("lunch_requested", 1)
    orm.status = kwargs.get("status", 1)
    orm.user_id = kwargs.get("user_id", None)
    orm.as_extra = kwargs.get("as_extra", 0)
    orm.not_come = kwargs.get("not_come", 0)
    orm.modify_user_id = kwargs.get("modify_user_id", None)
    orm.modify_date = kwargs.get("modify_date", None)
    orm.modify_notes = kwargs.get("modify_notes", "")
    return orm


class TestEarlyOrmToDomain:
    def test_maps_all_fields(self):
        orm = _make_early_orm(
            id=42,
            student_id=7,
            early_requested=1,
            early_plus_requested=1,
            status=1,
            as_extra=0,
            not_come=0,
            modify_notes="nota",
        )
        domain = early_orm_to_domain(orm)
        assert domain.id == 42
        assert domain.student_id == 7
        assert domain.early_requested == 1
        assert domain.early_plus_requested == 1
        assert domain.modify_notes == "nota"

    def test_datetime_to_date_conversion(self):
        orm = _make_early_orm(early_day=datetime(2026, 6, 1, 0, 0, 0))
        domain = early_orm_to_domain(orm)
        assert domain.early_day == date(2026, 6, 1)

    def test_none_fields_fallback_to_zero(self):
        orm = _make_early_orm(early_requested=None, early_plus_requested=None, as_extra=None, not_come=None)
        domain = early_orm_to_domain(orm)
        assert domain.early_requested == 0
        assert domain.early_plus_requested == 0
        assert domain.as_extra == 0
        assert domain.not_come == 0


class TestLunchOrmToDomain:
    def test_maps_all_fields(self):
        orm = _make_lunch_orm(
            id=99,
            student_id=5,
            lunch_requested=1,
            status=1,
            as_extra=1,
            not_come=0,
            modify_notes="",
        )
        domain = lunch_orm_to_domain(orm)
        assert domain.id == 99
        assert domain.student_id == 5
        assert domain.lunch_requested == 1
        assert domain.as_extra == 1

    def test_datetime_to_date_conversion(self):
        orm = _make_lunch_orm(lunch_day=datetime(2026, 6, 1, 0, 0, 0))
        domain = lunch_orm_to_domain(orm)
        assert domain.lunch_day == date(2026, 6, 1)

    def test_none_lunch_requested_fallback(self):
        orm = _make_lunch_orm(lunch_requested=None, as_extra=None, not_come=None)
        domain = lunch_orm_to_domain(orm)
        assert domain.lunch_requested == 0
        assert domain.as_extra == 0
        assert domain.not_come == 0


class TestToDateHelper:
    def test_none_returns_today(self):
        """_to_date(None) → date.today() (line 20)."""
        from datetime import date

        from app.infrastructure.attendance.mapper import _to_date

        result = _to_date(None)
        assert result == date.today()

    def test_plain_date_returned_as_is(self):
        """_to_date(date) → same date returned (line 23)."""
        from datetime import date

        from app.infrastructure.attendance.mapper import _to_date

        d = date(2026, 3, 15)
        result = _to_date(d)
        assert result == d
