"""
Tests de integración: SQLAlchemyLunchRepository contra SQLite in-memory.

REQ: R02 + R04
- test_save_creates_new_lunch_attendance
- test_find_by_student_and_date_returns_record
- test_list_by_school_and_date_returns_correct_records
- test_delete_soft_deletes
"""

from datetime import date

import pytest

from app.infrastructure.attendance.repository import SQLAlchemyLunchRepository
from tests.factories.lunch_orm_factory import LunchORMFactory
from tests.factories.student_orm_factory import StudentORMFactory


@pytest.fixture
def repo(app, db):
    with app.app_context():
        yield SQLAlchemyLunchRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    with app.app_context():
        LunchORMFactory._meta.sqlalchemy_session = db.session
        StudentORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestSaveLunchAttendance:
    def test_save_creates_new_record(self, repo, app):
        with app.app_context():
            from app.domain.attendance.lunch_attendance import LunchAttendance

            la = LunchAttendance(
                student_id=1,
                lunch_day=date(2026, 5, 1),
                lunch_requested=1,
                user_id=1,
            )
            saved = repo.save(la)
            assert saved.id is not None
            assert saved.lunch_requested == 1

    def test_save_updates_existing_record(self, repo, app):
        with app.app_context():
            orm = LunchORMFactory.create(lunch_requested=0, student_id=1)
            from app.domain.attendance.lunch_attendance import LunchAttendance

            la = LunchAttendance(
                id=orm.id,
                student_id=1,
                lunch_day=date(2026, 5, 2),
                lunch_requested=1,
            )
            updated = repo.save(la)
            assert updated.lunch_requested == 1


class TestFindLunchByStudentAndDate:
    def test_find_returns_record(self, repo, app):
        with app.app_context():
            day = date(2026, 5, 5)
            orm = LunchORMFactory.create(student_id=1, lunch_day=day, status=1)
            result = repo.find_by_student_and_date(1, day)
            assert result is not None
            assert result.id == orm.id

    def test_find_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.find_by_student_and_date(99999, date(2099, 1, 1))
            assert result is None


class TestListLunchBySchoolAndDate:
    def test_list_returns_correct_records(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(school_id=101, status=1)
            day = date(2026, 5, 12)
            LunchORMFactory.create(student_id=student.id, lunch_day=day, status=1)

            results = repo.list_by_school_and_date(school_id=101, day=day)
            student_ids = [r.student_id for r in results]
            assert student.id in student_ids

    def test_list_excludes_other_school(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(school_id=102, status=1)
            day = date(2026, 5, 13)
            LunchORMFactory.create(student_id=student.id, lunch_day=day, status=1)

            results = repo.list_by_school_and_date(school_id=103, day=day)
            student_ids = [r.student_id for r in results]
            assert student.id not in student_ids


class TestDeleteLunchAttendance:
    def test_delete_soft_deletes(self, repo, app):
        with app.app_context():
            orm = LunchORMFactory.create(student_id=1, status=1)
            repo.delete(orm.id)
            result = repo.find_by_student_and_date(
                orm.student_id, orm.lunch_day.date() if hasattr(orm.lunch_day, "date") else orm.lunch_day
            )
            assert result is None or result.status == 0


class TestListByDayNonExtraOnly:
    """Tests para non_extra_only=True — bug: as_extra=0 no se devolvía."""

    def test_non_extra_only_returns_records_with_as_extra_0(self, repo, app):
        """as_extra=0 (valor por defecto actual) debe ser devuelto."""
        with app.app_context():
            day = date(2026, 6, 1)
            LunchORMFactory.create(student_id=100, lunch_day=day, lunch_requested=1, as_extra=0)

            results = repo.list_by_day(day=day, non_extra_only=True)
            ids = [r.student_id for r in results]
            assert 100 in ids, "as_extra=0 debe ser incluido en non_extra_only=True"

    def test_non_extra_only_excludes_records_with_as_extra_1(self, repo, app):
        """as_extra=1 (extra) debe ser excluido."""
        with app.app_context():
            day = date(2026, 6, 2)
            LunchORMFactory.create(student_id=200, lunch_day=day, lunch_requested=1, as_extra=1)

            results = repo.list_by_day(day=day, non_extra_only=True)
            ids = [r.student_id for r in results]
            assert 200 not in ids, "as_extra=1 debe ser excluido con non_extra_only=True"

    def test_non_extra_only_returns_records_with_as_extra_none(self, repo, app):
        """as_extra=NULL (legacy) debe ser devuelto."""
        with app.app_context():
            day = date(2026, 6, 3)
            LunchORMFactory.create(student_id=300, lunch_day=day, lunch_requested=1, as_extra=None)

            results = repo.list_by_day(day=day, non_extra_only=True)
            ids = [r.student_id for r in results]
            assert 300 in ids, "as_extra=NULL debe ser incluido en non_extra_only=True"

    def test_non_extra_only_false_returns_all(self, repo, app):
        """non_extra_only=False debe devolver tanto 0 como 1."""
        with app.app_context():
            day = date(2026, 6, 4)
            LunchORMFactory.create(student_id=400, lunch_day=day, lunch_requested=1, as_extra=0)
            LunchORMFactory.create(student_id=401, lunch_day=day, lunch_requested=1, as_extra=1)
            LunchORMFactory.create(student_id=402, lunch_day=day, lunch_requested=1, as_extra=None)

            results = repo.list_by_day(day=day, non_extra_only=False)
            ids = [r.student_id for r in results]
            assert 400 in ids
            assert 401 in ids
            assert 402 in ids
