"""
Tests de integración: nuevos métodos de report en EarlyRepository y LunchRepository.

REQ-AR01: EarlyAttendanceRepository nuevos métodos
REQ-AR02: LunchAttendanceRepository nuevos métodos
"""

from datetime import date

import pytest

from app.infrastructure.attendance.repository import (
    SQLAlchemyEarlyRepository,
    SQLAlchemyLunchRepository,
)
from tests.factories.early_orm_factory import EarlyORMFactory
from tests.factories.lunch_orm_factory import LunchORMFactory
from tests.factories.student_orm_factory import StudentORMFactory


@pytest.fixture
def early_repo(app, db):
    with app.app_context():
        yield SQLAlchemyEarlyRepository()


@pytest.fixture
def lunch_repo(app, db):
    with app.app_context():
        yield SQLAlchemyLunchRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    with app.app_context():
        EarlyORMFactory._meta.sqlalchemy_session = db.session
        LunchORMFactory._meta.sqlalchemy_session = db.session
        StudentORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestEarlyListByDateRange:
    def test_returns_records_in_range_no_filter(self, early_repo, app):
        with app.app_context():
            d = date(2027, 1, 10)
            EarlyORMFactory.create(
                student_id=100,
                early_day=d,
                early_requested=1,
                early_plus_requested=0,
                status=1,
            )
            result = early_repo.list_by_date_range("2027-01-01", "2027-01-31")
            assert any(r.student_id == 100 for r in result)

    def test_excludes_records_outside_range(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=101,
                early_day=date(2027, 3, 1),
                early_requested=1,
                status=1,
            )
            result = early_repo.list_by_date_range("2027-01-01", "2027-01-31")
            assert all(r.student_id != 101 for r in result)

    def test_type_filter_early_only(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=102,
                early_day=date(2027, 2, 5),
                early_requested=1,
                early_plus_requested=0,
                status=1,
            )
            EarlyORMFactory.create(
                student_id=103,
                early_day=date(2027, 2, 5),
                early_requested=0,
                early_plus_requested=1,
                status=1,
            )
            result = early_repo.list_by_date_range("2027-02-01", "2027-02-28", type_filter="early")
            ids = [r.student_id for r in result]
            assert 102 in ids
            assert 103 not in ids

    def test_type_filter_early_plus_only(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=104,
                early_day=date(2027, 2, 6),
                early_requested=1,
                early_plus_requested=0,
                status=1,
            )
            EarlyORMFactory.create(
                student_id=105,
                early_day=date(2027, 2, 6),
                early_requested=0,
                early_plus_requested=1,
                status=1,
            )
            result = early_repo.list_by_date_range("2027-02-01", "2027-02-28", type_filter="early_plus")
            ids = [r.student_id for r in result]
            assert 105 in ids
            assert 104 not in ids

    def test_student_id_filter(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=106,
                early_day=date(2027, 2, 7),
                early_requested=1,
                status=1,
            )
            EarlyORMFactory.create(
                student_id=107,
                early_day=date(2027, 2, 7),
                early_requested=1,
                status=1,
            )
            result = early_repo.list_by_date_range("2027-02-01", "2027-02-28", student_id=106)
            assert all(r.student_id == 106 for r in result)


class TestEarlyListByDay:
    def test_returns_records_for_day(self, early_repo, app):
        with app.app_context():
            d = date(2027, 4, 1)
            EarlyORMFactory.create(
                student_id=110,
                early_day=d,
                early_requested=1,
                early_plus_requested=0,
            )
            result = early_repo.list_by_day(day=d)
            assert any(r.student_id == 110 for r in result)

    def test_excludes_other_days(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=111,
                early_day=date(2027, 4, 2),
                early_requested=1,
            )
            result = early_repo.list_by_day(day=date(2027, 4, 3))
            assert all(r.student_id != 111 for r in result)

    def test_plus_only_filter(self, early_repo, app):
        with app.app_context():
            d = date(2027, 4, 5)
            EarlyORMFactory.create(
                student_id=112,
                early_day=d,
                early_requested=1,
                early_plus_requested=0,
            )
            EarlyORMFactory.create(
                student_id=113,
                early_day=d,
                early_requested=0,
                early_plus_requested=1,
            )
            result = early_repo.list_by_day(day=d, type_filter="plus_only")
            ids = [r.student_id for r in result]
            assert 113 in ids
            assert 112 not in ids


class TestLunchListByDateRange:
    def test_returns_records_in_range(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(
                student_id=120,
                lunch_day=date(2027, 1, 15),
                lunch_requested=1,
                status=1,
            )
            result = lunch_repo.list_by_date_range("2027-01-01", "2027-01-31")
            assert any(r.student_id == 120 for r in result)

    def test_excludes_outside_range(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(
                student_id=121,
                lunch_day=date(2027, 3, 1),
                lunch_requested=1,
                status=1,
            )
            result = lunch_repo.list_by_date_range("2027-01-01", "2027-01-31")
            assert all(r.student_id != 121 for r in result)

    def test_student_id_filter(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(
                student_id=122,
                lunch_day=date(2027, 2, 10),
                lunch_requested=1,
                status=1,
            )
            LunchORMFactory.create(
                student_id=123,
                lunch_day=date(2027, 2, 10),
                lunch_requested=1,
                status=1,
            )
            result = lunch_repo.list_by_date_range("2027-02-01", "2027-02-28", student_id=122)
            assert all(r.student_id == 122 for r in result)


class TestLunchListByDay:
    def test_returns_lunch_requested_for_day(self, lunch_repo, app):
        with app.app_context():
            d = date(2027, 5, 1)
            LunchORMFactory.create(student_id=130, lunch_day=d, lunch_requested=1)
            result = lunch_repo.list_by_day(day=d)
            assert any(r.student_id == 130 for r in result)

    def test_excludes_other_days(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(student_id=131, lunch_day=date(2027, 5, 2), lunch_requested=1)
            result = lunch_repo.list_by_day(day=date(2027, 5, 3))
            assert all(r.student_id != 131 for r in result)

    def test_non_extra_only_excludes_extras(self, lunch_repo, app):
        with app.app_context():
            d = date(2027, 5, 5)
            # as_extra=None → included; as_extra=1 → excluded
            LunchORMFactory.create(student_id=132, lunch_day=d, lunch_requested=1, as_extra=None)
            LunchORMFactory.create(student_id=133, lunch_day=d, lunch_requested=1, as_extra=1)
            result = lunch_repo.list_by_day(day=d, non_extra_only=True)
            ids = [r.student_id for r in result]
            assert 132 in ids
            assert 133 not in ids
