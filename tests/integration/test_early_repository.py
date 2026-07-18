"""
Tests de integración: SQLAlchemyEarlyRepository contra SQLite in-memory.

REQ: R01 + R03
- test_save_creates_new_early_attendance
- test_find_by_student_and_date_returns_record
- test_list_by_school_and_date_returns_correct_records
- test_delete_soft_deletes
"""

from datetime import date

import pytest

from app.infrastructure.attendance.repository import SQLAlchemyEarlyRepository
from tests.factories.early_orm_factory import EarlyORMFactory
from tests.factories.student_orm_factory import StudentORMFactory


@pytest.fixture
def repo(app, db):
    with app.app_context():
        yield SQLAlchemyEarlyRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    with app.app_context():
        EarlyORMFactory._meta.sqlalchemy_session = db.session
        StudentORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestSaveEarlyAttendance:
    def test_save_creates_new_record(self, repo, app):
        with app.app_context():
            from app.domain.attendance.early_attendance import EarlyAttendance

            ea = EarlyAttendance(
                student_id=1,
                early_day=date(2026, 5, 1),
                early_requested=1,
                early_plus_requested=0,
                user_id=1,
            )
            saved = repo.save(ea)
            assert saved.id is not None
            assert saved.early_requested == 1

    def test_save_updates_existing_record(self, repo, app):
        with app.app_context():
            orm = EarlyORMFactory.create(early_requested=0, student_id=1)
            from app.domain.attendance.early_attendance import EarlyAttendance

            ea = EarlyAttendance(
                id=orm.id,
                student_id=1,
                early_day=date(2026, 5, 2),
                early_requested=1,
                early_plus_requested=0,
            )
            updated = repo.save(ea)
            assert updated.early_requested == 1


class TestFindByStudentAndDate:
    def test_find_returns_record(self, repo, app):
        with app.app_context():
            day = date(2026, 5, 5)
            orm = EarlyORMFactory.create(student_id=1, early_day=day, status=1)
            result = repo.find_by_student_and_date(1, day)
            assert result is not None
            assert result.id == orm.id

    def test_find_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.find_by_student_and_date(99999, date(2099, 1, 1))
            assert result is None


class TestListBySchoolAndDate:
    def test_list_returns_correct_records(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(school_id=77, status=1)
            day = date(2026, 5, 10)
            EarlyORMFactory.create(student_id=student.id, early_day=day, status=1)

            results = repo.list_by_school_and_date(school_id=77, day=day)
            student_ids = [r.student_id for r in results]
            assert student.id in student_ids

    def test_list_excludes_other_school(self, repo, app, db):
        with app.app_context():
            student = StudentORMFactory.create(school_id=88, status=1)
            day = date(2026, 5, 11)
            EarlyORMFactory.create(student_id=student.id, early_day=day, status=1)

            results = repo.list_by_school_and_date(school_id=99, day=day)
            student_ids = [r.student_id for r in results]
            assert student.id not in student_ids


class TestDeleteEarlyAttendance:
    def test_delete_soft_deletes(self, repo, app):
        with app.app_context():
            orm = EarlyORMFactory.create(student_id=1, status=1)
            repo.delete(orm.id)
            result = repo.find_by_student_and_date(
                orm.student_id, orm.early_day.date() if hasattr(orm.early_day, "date") else orm.early_day
            )
            # Deleted record shouldn't show up in active query
            assert result is None or result.status == 0
