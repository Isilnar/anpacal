"""
Tests de integración: list_by_student_ids_from_date para Early y Lunch repositories.

REQ-AC01: EarlyAttendanceRepository.list_by_student_ids_from_date
REQ-AC02: LunchAttendanceRepository.list_by_student_ids_from_date
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


class TestEarlyListByStudentIdsFromDate:
    def test_returns_empty_for_empty_ids(self, early_repo, app):
        with app.app_context():
            result = early_repo.list_by_student_ids_from_date([], date(2026, 5, 1))
            assert result == []

    def test_returns_records_from_date_inclusive(self, early_repo, app):
        with app.app_context():
            from_date = date(2026, 6, 1)
            after = date(2026, 6, 10)
            EarlyORMFactory.create(student_id=50, early_day=after, early_requested=1, status=1)
            result = early_repo.list_by_student_ids_from_date([50], from_date)
            assert any(r.student_id == 50 for r in result)

    def test_excludes_records_before_from_date(self, early_repo, app):
        with app.app_context():
            from_date = date(2026, 6, 15)
            before = date(2026, 6, 5)
            EarlyORMFactory.create(student_id=51, early_day=before, early_requested=1, status=1)
            result = early_repo.list_by_student_ids_from_date([51], from_date)
            # If any result for student 51, its date must be >= from_date
            for r in result:
                if r.student_id == 51:
                    assert r.early_day >= from_date

    def test_includes_record_on_exact_from_date(self, early_repo, app):
        with app.app_context():
            exact_date = date(2026, 7, 1)
            EarlyORMFactory.create(student_id=52, early_day=exact_date, early_requested=1, status=1)
            result = early_repo.list_by_student_ids_from_date([52], exact_date)
            assert any(r.student_id == 52 and r.early_day == exact_date for r in result)

    def test_excludes_inactive_records(self, early_repo, app):
        with app.app_context():
            from_date = date(2026, 8, 1)
            after = date(2026, 8, 10)
            EarlyORMFactory.create(student_id=53, early_day=after, early_requested=1, status=0)
            result = early_repo.list_by_student_ids_from_date([53], from_date)
            assert all(r.status == 1 for r in result)

    def test_excludes_other_students(self, early_repo, app):
        with app.app_context():
            from_date = date(2026, 9, 1)
            after = date(2026, 9, 10)
            EarlyORMFactory.create(student_id=54, early_day=after, early_requested=1, status=1)
            result = early_repo.list_by_student_ids_from_date([99999], from_date)
            assert all(r.student_id != 54 for r in result)

    def test_returns_multiple_students(self, early_repo, app):
        with app.app_context():
            from_date = date(2026, 10, 1)
            EarlyORMFactory.create(student_id=55, early_day=date(2026, 10, 5), early_requested=1, status=1)
            EarlyORMFactory.create(student_id=56, early_day=date(2026, 10, 6), early_requested=1, status=1)
            result = early_repo.list_by_student_ids_from_date([55, 56], from_date)
            student_ids = [r.student_id for r in result]
            assert 55 in student_ids
            assert 56 in student_ids


class TestLunchListByStudentIdsFromDate:
    def test_returns_empty_for_empty_ids(self, lunch_repo, app):
        with app.app_context():
            result = lunch_repo.list_by_student_ids_from_date([], date(2026, 5, 1))
            assert result == []

    def test_returns_records_from_date_inclusive(self, lunch_repo, app):
        with app.app_context():
            from_date = date(2026, 6, 1)
            after = date(2026, 6, 10)
            LunchORMFactory.create(student_id=60, lunch_day=after, lunch_requested=1, status=1)
            result = lunch_repo.list_by_student_ids_from_date([60], from_date)
            assert any(r.student_id == 60 for r in result)

    def test_excludes_records_before_from_date(self, lunch_repo, app):
        with app.app_context():
            from_date = date(2026, 6, 15)
            before = date(2026, 6, 5)
            LunchORMFactory.create(student_id=61, lunch_day=before, lunch_requested=1, status=1)
            result = lunch_repo.list_by_student_ids_from_date([61], from_date)
            for r in result:
                if r.student_id == 61:
                    assert r.lunch_day >= from_date

    def test_includes_record_on_exact_from_date(self, lunch_repo, app):
        with app.app_context():
            exact_date = date(2026, 7, 1)
            LunchORMFactory.create(student_id=62, lunch_day=exact_date, lunch_requested=1, status=1)
            result = lunch_repo.list_by_student_ids_from_date([62], exact_date)
            assert any(r.student_id == 62 and r.lunch_day == exact_date for r in result)

    def test_excludes_inactive_records(self, lunch_repo, app):
        with app.app_context():
            from_date = date(2026, 8, 1)
            after = date(2026, 8, 10)
            LunchORMFactory.create(student_id=63, lunch_day=after, lunch_requested=1, status=0)
            result = lunch_repo.list_by_student_ids_from_date([63], from_date)
            assert all(r.status == 1 for r in result)

    def test_excludes_other_students(self, lunch_repo, app):
        with app.app_context():
            from_date = date(2026, 9, 1)
            after = date(2026, 9, 10)
            LunchORMFactory.create(student_id=64, lunch_day=after, lunch_requested=1, status=1)
            result = lunch_repo.list_by_student_ids_from_date([99999], from_date)
            assert all(r.student_id != 64 for r in result)

    def test_returns_multiple_students(self, lunch_repo, app):
        with app.app_context():
            from_date = date(2026, 10, 1)
            LunchORMFactory.create(student_id=65, lunch_day=date(2026, 10, 5), lunch_requested=1, status=1)
            LunchORMFactory.create(student_id=66, lunch_day=date(2026, 10, 6), lunch_requested=1, status=1)
            result = lunch_repo.list_by_student_ids_from_date([65, 66], from_date)
            student_ids = [r.student_id for r in result]
            assert 65 in student_ids
            assert 66 in student_ids
