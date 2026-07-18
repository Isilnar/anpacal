"""
Tests de integración: find_by_id, search para EarlyRepository y LunchRepository,
y get_student_ids_by_user para SQLAlchemyUserRepository.

REQ-ER01, REQ-ER02, REQ-ER03, REQ-ER04
"""

from datetime import date

import pytest

from app.infrastructure.attendance.repository import (
    SQLAlchemyEarlyRepository,
    SQLAlchemyLunchRepository,
)
from app.infrastructure.user.repository import SQLAlchemyUserRepository
from tests.factories.early_orm_factory import EarlyORMFactory
from tests.factories.lunch_orm_factory import LunchORMFactory
from tests.factories.student_orm_factory import StudentORMFactory
from tests.factories.user_orm_factory import UserORMFactory


@pytest.fixture
def early_repo(app, db):
    with app.app_context():
        yield SQLAlchemyEarlyRepository()


@pytest.fixture
def lunch_repo(app, db):
    with app.app_context():
        yield SQLAlchemyLunchRepository()


@pytest.fixture
def user_repo(app, db):
    with app.app_context():
        yield SQLAlchemyUserRepository()


@pytest.fixture(autouse=True)
def setup_factory_sessions(app, db):
    with app.app_context():
        EarlyORMFactory._meta.sqlalchemy_session = db.session
        LunchORMFactory._meta.sqlalchemy_session = db.session
        StudentORMFactory._meta.sqlalchemy_session = db.session
        UserORMFactory._meta.sqlalchemy_session = db.session
        yield


# ---------------------------------------------------------------------------
# EarlyRepository.find_by_id
# ---------------------------------------------------------------------------


class TestEarlyFindById:
    def test_returns_entity_when_found(self, early_repo, app):
        with app.app_context():
            orm = EarlyORMFactory.create(student_id=200, early_requested=1)
            result = early_repo.find_by_id(orm.id)
            assert result is not None
            assert result.id == orm.id
            assert result.student_id == 200

    def test_returns_none_when_not_found(self, early_repo, app):
        with app.app_context():
            result = early_repo.find_by_id(999999)
            assert result is None


# ---------------------------------------------------------------------------
# EarlyRepository.search
# ---------------------------------------------------------------------------


class TestEarlySearch:
    def test_returns_records_within_date_range(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=201,
                early_day=date(2028, 2, 10),
                early_requested=1,
                status=1,
            )
            result = early_repo.search(
                student_id=0,
                user_student_ids=[],
                date_from="2028-02-01",
                date_until="2028-02-28",
            )
            assert any(r.student_id == 201 for r in result)

    def test_excludes_records_outside_range(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=202,
                early_day=date(2028, 4, 1),
                early_requested=1,
                status=1,
            )
            result = early_repo.search(
                student_id=0,
                user_student_ids=[],
                date_from="2028-02-01",
                date_until="2028-02-28",
            )
            assert all(r.student_id != 202 for r in result)

    def test_filters_by_student_id(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=203,
                early_day=date(2028, 3, 5),
                early_requested=1,
                status=1,
            )
            EarlyORMFactory.create(
                student_id=204,
                early_day=date(2028, 3, 5),
                early_requested=1,
                status=1,
            )
            result = early_repo.search(
                student_id=203,
                user_student_ids=[],
                date_from="2028-03-01",
                date_until="2028-03-31",
            )
            assert all(r.student_id == 203 for r in result)
            assert any(r.student_id == 203 for r in result)

    def test_filters_by_user_student_ids(self, early_repo, app):
        with app.app_context():
            EarlyORMFactory.create(
                student_id=205,
                early_day=date(2028, 3, 6),
                early_requested=1,
                status=1,
            )
            EarlyORMFactory.create(
                student_id=206,
                early_day=date(2028, 3, 6),
                early_requested=1,
                status=1,
            )
            result = early_repo.search(
                student_id=0,
                user_student_ids=[205],
                date_from="2028-03-01",
                date_until="2028-03-31",
            )
            ids = [r.student_id for r in result]
            assert 205 in ids
            assert 206 not in ids


# ---------------------------------------------------------------------------
# LunchRepository.find_by_id
# ---------------------------------------------------------------------------


class TestLunchFindById:
    def test_returns_entity_when_found(self, lunch_repo, app):
        with app.app_context():
            orm = LunchORMFactory.create(student_id=210, lunch_requested=1)
            result = lunch_repo.find_by_id(orm.id)
            assert result is not None
            assert result.id == orm.id
            assert result.student_id == 210

    def test_returns_none_when_not_found(self, lunch_repo, app):
        with app.app_context():
            result = lunch_repo.find_by_id(888888)
            assert result is None


# ---------------------------------------------------------------------------
# LunchRepository.search
# ---------------------------------------------------------------------------


class TestLunchSearch:
    def test_returns_records_within_date_range(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(
                student_id=211,
                lunch_day=date(2028, 5, 10),
                lunch_requested=1,
                status=1,
            )
            result = lunch_repo.search(
                student_id=0,
                user_student_ids=[],
                date_from="2028-05-01",
                date_until="2028-05-31",
            )
            assert any(r.student_id == 211 for r in result)

    def test_excludes_records_outside_range(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(
                student_id=212,
                lunch_day=date(2028, 7, 1),
                lunch_requested=1,
                status=1,
            )
            result = lunch_repo.search(
                student_id=0,
                user_student_ids=[],
                date_from="2028-05-01",
                date_until="2028-05-31",
            )
            assert all(r.student_id != 212 for r in result)

    def test_filters_by_student_id(self, lunch_repo, app):
        with app.app_context():
            LunchORMFactory.create(
                student_id=213,
                lunch_day=date(2028, 5, 12),
                lunch_requested=1,
                status=1,
            )
            LunchORMFactory.create(
                student_id=214,
                lunch_day=date(2028, 5, 12),
                lunch_requested=1,
                status=1,
            )
            result = lunch_repo.search(
                student_id=213,
                user_student_ids=[],
                date_from="2028-05-01",
                date_until="2028-05-31",
            )
            assert all(r.student_id == 213 for r in result)


# ---------------------------------------------------------------------------
# UserRepository.get_student_ids_by_user
# ---------------------------------------------------------------------------


class TestGetStudentIdsByUser:
    def test_returns_student_ids_for_user(self, user_repo, app, db):
        with app.app_context():
            from app.infrastructure.student.orm import StudentORM
            from app.infrastructure.user.orm import UserORM, UserStudentAssociation

            student = StudentORMFactory.create()
            user = UserORMFactory.create()

            assoc = UserStudentAssociation(user_id=user.id, student_id=student.id)
            db.session.add(assoc)
            db.session.commit()

            result = user_repo.get_student_ids_by_user(user.id)
            assert student.id in result

    def test_returns_empty_list_when_no_associations(self, user_repo, app):
        with app.app_context():
            user = UserORMFactory.create()
            result = user_repo.get_student_ids_by_user(user.id)
            assert result == []
