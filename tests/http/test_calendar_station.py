"""
Tests HTTP para el endpoint /load_calendar_event (Blueprint calendar_station).

REQ-CS02: el route delega en GetDayAttendanceByStudentsUseCase.
REQ-CS03: el JSON de respuesta tiene exactamente current_date, locale_date,
          current_students_data con id/fullname/early/early_plus/lunch.
"""

from unittest.mock import MagicMock, patch

import pytest


def _setup_session(client, user_id: str):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id
        sess["_fresh"] = True


def _make_student_assoc(student_id: int, name: str, surname: str, school_id: int):
    """Construye un mock de UserStudentAssociation con student embebido."""
    student_mock = MagicMock()
    student_mock.id = student_id
    student_mock.name = name
    student_mock.surname = surname
    student_mock.school_id = school_id

    assoc_mock = MagicMock()
    assoc_mock.student = student_mock
    return assoc_mock


class TestLoadCalendarEventAuth:
    def test_requires_login(self, client):
        """POST /load_calendar_event sin sesión → 302 (login required)."""
        response = client.post(
            "/load_calendar_event",
            json={"current_event_date": "2026-05-12", "center_id": 1},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)


class TestLoadCalendarEventResponseShape:
    def test_returns_200_with_correct_shape(self, client, app, db):
        """POST /load_calendar_event con sesión válida → 200 + JSON con shape correcto."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        center_id = 1
        student_assoc = _make_student_assoc(student_id=10, name="Ana", surname="García", school_id=center_id)

        with (
            patch(
                "app.application.attendance.get_day_attendance_by_students.GetDayAttendanceByStudentsUseCase"
            ) as mock_uc,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
        ):
            mock_cu.students = [student_assoc]
            mock_uc.return_value.execute.return_value = [{"id": 10, "early": 1, "early_plus": 0, "lunch": 1}]

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/load_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": center_id},
                )

        assert response.status_code == 200
        data = response.get_json()
        assert "current_date" in data
        assert "locale_date" in data
        assert "current_students_data" in data
        assert len(data["current_students_data"]) == 1
        entry = data["current_students_data"][0]
        assert set(entry.keys()) == {"id", "fullname", "early", "early_plus", "lunch"}

    def test_student_entry_fields(self, client, app, db):
        """Cada entrada de current_students_data tiene exactamente id/fullname/early/early_plus/lunch."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        center_id = 2
        student_assoc = _make_student_assoc(student_id=99, name="Pedro", surname="López", school_id=center_id)

        with (
            patch(
                "app.application.attendance.get_day_attendance_by_students.GetDayAttendanceByStudentsUseCase"
            ) as mock_uc,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
        ):
            mock_cu.students = [student_assoc]
            mock_uc.return_value.execute.return_value = [{"id": 99, "early": 0, "early_plus": 1, "lunch": 0}]

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/load_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": center_id},
                )

        data = response.get_json()
        entry = data["current_students_data"][0]
        assert entry["id"] == 99
        assert entry["fullname"] == "Pedro López"
        assert entry["early"] == 0
        assert entry["early_plus"] == 1
        assert entry["lunch"] == 0

    def test_use_case_called_once_with_student_ids_and_day(self, client, app, db):
        """El use case es invocado exactamente una vez con student_ids y day."""
        from datetime import date

        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        center_id = 3
        student_assoc = _make_student_assoc(student_id=5, name="María", surname="Fernández", school_id=center_id)

        with (
            patch(
                "app.application.attendance.get_day_attendance_by_students.GetDayAttendanceByStudentsUseCase"
            ) as mock_uc_cls,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
        ):
            mock_cu.students = [student_assoc]
            mock_uc_cls.return_value.execute.return_value = [{"id": 5, "early": 1, "early_plus": 0, "lunch": 0}]

            _setup_session(client, user_id)
            with app.app_context():
                client.post(
                    "/load_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": center_id},
                )

        mock_uc_cls.return_value.execute.assert_called_once_with([5], date(2026, 5, 12))


class TestLoadCalendarEventEmptyStudents:
    def test_empty_students_returns_empty_array(self, client, app, db):
        """REQ-CS03 scenario: centro sin alumnos → current_students_data=[]."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch(
                "app.application.attendance.get_day_attendance_by_students.GetDayAttendanceByStudentsUseCase"
            ) as mock_uc,
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
        ):
            mock_cu.students = []  # no students in this center
            mock_uc.return_value.execute.return_value = []

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/load_calendar_event",
                    json={"current_event_date": "2026-05-12", "center_id": 1},
                )

        assert response.status_code == 200
        data = response.get_json()
        assert "current_date" in data
        assert "locale_date" in data
        assert data["current_students_data"] == []
