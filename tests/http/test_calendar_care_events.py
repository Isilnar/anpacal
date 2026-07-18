"""
Tests HTTP para los endpoints /load_earlycare_calendar_event y
/load_lunchcare_calendar_event (Blueprint calendar_station).

REQ-EL02/REQ-EL03: rutas POST @login_required que delegan en
GetCareCalendarEventUseCase y retornan el JSON de 9 keys (REQ-EL04).
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.application.attendance.get_care_calendar_event import CareCalendarEventDTO


def _setup_session(client, user_id: str):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id
        sess["_fresh"] = True


def _make_dto(**kwargs):
    """Returns a CareCalendarEventDTO with sensible test defaults."""
    defaults = dict(
        almuerzo_total=3,
        almuerzo_infantil=1,
        almuerzo_primaria=2,
        almuerzo_intolerances="1 alerxia/s gluten",
        comedor_total=5,
        comedor_infantil=2,
        comedor_primaria=3,
        comedor_intolerances="",
    )
    defaults.update(kwargs)
    return CareCalendarEventDTO(**defaults)


_EXPECTED_KEYS = {
    "locale_date",
    "lunchcare_almuerzo",
    "almorzo_infantil",
    "almorzo_primaria",
    "lunchcare_almuerzo_intolerances",
    "lunchcare_comedor",
    "comedor_infantil",
    "comedor_primaria",
    "lunchcare_comedor_intolerances",
}


class TestLoadEarlycareCalendarEventAuth:
    def test_requires_login(self, client):
        """POST /load_earlycare_calendar_event sin sesión → 302."""
        response = client.post(
            "/load_earlycare_calendar_event",
            json={"current_event_date": "2026-05-12", "center_id": 1},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)


class TestLoadLunchcareCalendarEventAuth:
    def test_requires_login(self, client):
        """POST /load_lunchcare_calendar_event sin sesión → 302."""
        response = client.post(
            "/load_lunchcare_calendar_event",
            json={"current_event_date": "2026-05-12", "center_id": 1},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)


class TestLoadEarlycareCalendarEventResponse:
    def test_returns_200_with_correct_shape(self, client, app, db):
        """POST /load_earlycare_calendar_event → 200 + todos los 9 keys JSON."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.application.attendance.get_care_calendar_event.GetCareCalendarEventUseCase") as mock_uc,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.student.repository.SQLAlchemyStudentRepository"),
            patch("app.infrastructure.intolerance.repository.SQLAlchemyDietIntoleranceRepository"),
        ):
            mock_uc.return_value.execute.return_value = _make_dto()

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/load_earlycare_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": 1},
                )

        assert response.status_code == 200
        data = response.get_json()
        assert set(data.keys()) == _EXPECTED_KEYS

    def test_use_case_called_once(self, client, app, db):
        """El use case se llama exactamente una vez con (center_id, day)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        center_id = 42

        with (
            patch("app.application.attendance.get_care_calendar_event.GetCareCalendarEventUseCase") as mock_uc_cls,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.student.repository.SQLAlchemyStudentRepository"),
            patch("app.infrastructure.intolerance.repository.SQLAlchemyDietIntoleranceRepository"),
        ):
            mock_uc_cls.return_value.execute.return_value = _make_dto()

            _setup_session(client, user_id)
            with app.app_context():
                client.post(
                    "/load_earlycare_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": center_id},
                )

        mock_uc_cls.return_value.execute.assert_called_once_with(center_id, date(2026, 5, 12))


class TestLoadLunchcareCalendarEventResponse:
    def test_returns_200_with_correct_shape(self, client, app, db):
        """POST /load_lunchcare_calendar_event → 200 + todos los 9 keys JSON."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.application.attendance.get_care_calendar_event.GetCareCalendarEventUseCase") as mock_uc,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.student.repository.SQLAlchemyStudentRepository"),
            patch("app.infrastructure.intolerance.repository.SQLAlchemyDietIntoleranceRepository"),
        ):
            mock_uc.return_value.execute.return_value = _make_dto()

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/load_lunchcare_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": 1},
                )

        assert response.status_code == 200
        data = response.get_json()
        assert set(data.keys()) == _EXPECTED_KEYS

    def test_use_case_called_once(self, client, app, db):
        """El use case se llama exactamente una vez con (center_id, day)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        center_id = 7

        with (
            patch("app.application.attendance.get_care_calendar_event.GetCareCalendarEventUseCase") as mock_uc_cls,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.student.repository.SQLAlchemyStudentRepository"),
            patch("app.infrastructure.intolerance.repository.SQLAlchemyDietIntoleranceRepository"),
        ):
            mock_uc_cls.return_value.execute.return_value = _make_dto()

            _setup_session(client, user_id)
            with app.app_context():
                client.post(
                    "/load_lunchcare_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": center_id},
                )

        mock_uc_cls.return_value.execute.assert_called_once_with(center_id, date(2026, 5, 12))
