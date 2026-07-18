"""
Tests HTTP para calendar_routes (Blueprint calendar_bp, prefix /calendar).

REQ: V01 + V02
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


def _setup_session(client, user_id: str):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id
        sess["_fresh"] = True


class TestCalendarEventsRoute:
    def test_get_events_returns_200(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.adapters.views.calendar_routes.GetCalendarEventsUseCase") as mock_uc,
            patch("app.adapters.views.calendar_routes.SQLAlchemyEarlyRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyStudentRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyHolydayRepository"),
        ):
            mock_uc.return_value.execute.return_value = []
            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/calendar/events?school_id=1&date=2026-03-15")
        assert response.status_code == 200

    def test_get_events_requires_login(self, client):
        response = client.get("/calendar/events?school_id=1&date=2026-03-15", follow_redirects=False)
        assert response.status_code in (301, 302)


class TestEarlycareStatsRoute:
    def test_get_earlycare_stats_returns_200(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        from app.application.attendance.get_earlycare_stats import EarlycareStats

        with (
            patch("app.adapters.views.calendar_routes.GetEarlycareStatsUseCase") as mock_uc,
            patch("app.adapters.views.calendar_routes.SQLAlchemyEarlyRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyHolydayRepository"),
        ):
            mock_uc.return_value.execute.return_value = EarlycareStats()
            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/calendar/earlycare-stats?school_id=1&date=2026-03-15")
        assert response.status_code == 200

    def test_get_earlycare_stats_json_shape(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        from app.application.attendance.get_earlycare_stats import EarlycareStats

        with (
            patch("app.adapters.views.calendar_routes.GetEarlycareStatsUseCase") as mock_uc,
            patch("app.adapters.views.calendar_routes.SQLAlchemyEarlyRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyHolydayRepository"),
        ):
            mock_uc.return_value.execute.return_value = EarlycareStats(total_requested=3, total_not_come=1)
            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/calendar/earlycare-stats?school_id=1&date=2026-03-15")
        data = response.get_json()
        assert "total_requested" in data
        assert "total_not_come" in data


class TestLunchcareStatsRoute:
    def test_get_lunchcare_stats_returns_200(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        from app.application.attendance.get_lunchcare_stats import LunchcareStats

        with (
            patch("app.adapters.views.calendar_routes.GetLunchcareStatsUseCase") as mock_uc,
            patch("app.adapters.views.calendar_routes.SQLAlchemyEarlyRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyHolydayRepository"),
        ):
            mock_uc.return_value.execute.return_value = LunchcareStats()
            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/calendar/lunchcare-stats?school_id=1&date=2026-03-15")
        assert response.status_code == 200


class TestSaveAttendanceRangeRoute:
    def test_post_save_returns_200(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        from app.application.attendance.save_attendance_range import SaveAttendanceRangeResult

        with (
            patch("app.adapters.views.calendar_routes.SaveAttendanceRangeUseCase") as mock_uc,
            patch("app.adapters.views.calendar_routes.SQLAlchemyEarlyRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_routes.SQLAlchemyHolydayRepository"),
        ):
            mock_uc.return_value.execute.return_value = SaveAttendanceRangeResult(
                saved_dates=[date(2026, 3, 16)],
                skipped_dates=[],
            )
            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/calendar/attendance-range",
                    json={
                        "school_id": 1,
                        "date_from": "2026-03-16",
                        "date_to": "2026-03-20",
                        "attendances": [{"student_id": 1, "early_requested": 1, "lunch_requested": 1}],
                    },
                )
        assert response.status_code == 200
        data = response.get_json()
        assert "saved_dates" in data
        assert "skipped_dates" in data

    def test_post_invalid_dates_returns_422(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        _setup_session(client, user_id)
        with app.app_context():
            response = client.post(
                "/calendar/attendance-range",
                json={
                    "school_id": 1,
                    "date_from": "2026-03-20",
                    "date_to": "2026-03-16",  # date_to < date_from
                    "attendances": [],
                },
            )
        assert response.status_code == 422

    def test_post_missing_dates_returns_422(self, client, app, db):
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        _setup_session(client, user_id)
        with app.app_context():
            response = client.post("/calendar/attendance-range", json={"school_id": 1})
        assert response.status_code == 422
