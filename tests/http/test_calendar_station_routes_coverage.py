"""
Tests de cobertura HTTP para calendar_station_routes.py.

Cubre las líneas: 28-57, 63-83, 89-96, 108-128, 134-141, 153-160, 231-297

- management_calendar_post()        GET /management_calendar
- management_earlycare_calendar_post() GET /management_earlycare_calendar
- management_earlycare_calendar()   POST /management_earlycare_calendar
- management_lunchcare_calendar_post() GET /management_lunchcare_calendar
- management_lunchcare_calendar()   POST /management_lunchcare_calendar
- management_calendar()             POST /management_calendar
- save_calendar_event()             POST /save_calendar_event

NOTA: GetSchoolsByIdsUseCase y SaveAttendanceRangeUseCase se importan DENTRO
de cada función (lazy import), así que se parchean en sus módulos de origen.
"""

from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_session(client, user_id: str):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id
        sess["_fresh"] = True


def _make_school_mock(school_id: int):
    """Construye un mock de School domain object."""
    school_mock = MagicMock()
    school_mock.id = school_id
    school_mock.name = f"School {school_id}"
    return school_mock


def _make_student_assoc_mock(student_id: int, school_id: int):
    """Construye un mock de UserStudentAssociation con student embebido."""
    student_mock = MagicMock()
    student_mock.id = student_id
    student_mock.name = "Ana"
    student_mock.surname = "García"
    student_mock.school_id = school_id

    assoc_mock = MagicMock()
    assoc_mock.student = student_mock
    return assoc_mock


# ---------------------------------------------------------------------------
# GET /management_calendar (lines 28-57)
# ---------------------------------------------------------------------------


class TestManagementCalendarGet:
    def test_requires_login(self, client):
        """GET /management_calendar sin sesión → 302."""
        response = client.get("/management_calendar", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_one_school_renders_calendar(self, client, app, db):
        """GET /management_calendar con 1 escuela → calendar.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school_mock = _make_school_mock(school_id=1)
        student_assoc = _make_student_assoc_mock(student_id=10, school_id=1)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[school_mock],
            ),
            patch(
                "app.infrastructure.school.repository.SQLAlchemySchoolRepository.get_by_id",
                return_value=school_mock,
            ),
            patch("app.adapters.views.calendar_station_routes.get_calendar_events", return_value=[]),
            patch("app.adapters.views.calendar_station_routes.get_calendar_start_date", return_value="2026-01-15"),
            patch("app.adapters.views.calendar_station_routes.get_disabled_dates", return_value=[]),
            patch("app.adapters.views.calendar_station_routes.get_disabled_dates_reversed", return_value=[]),
            patch("app.adapters.views.calendar_station_routes.get_dates_between", return_value=[]),
        ):
            mock_cu.students = [student_assoc]
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_calendar")

        assert response.status_code == 200

    def test_zero_schools_renders_calendar_list(self, client, app, db):
        """GET /management_calendar con 0 escuelas → calendar_list.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[],
            ),
            patch("app.infrastructure.school.repository.SQLAlchemySchoolRepository"),
        ):
            mock_cu.students = []
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_calendar")

        assert response.status_code == 200

    def test_two_schools_renders_calendar_list(self, client, app, db):
        """GET /management_calendar con 2 escuelas → calendar_list.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school1 = _make_school_mock(school_id=1)
        school2 = _make_school_mock(school_id=2)
        student1 = _make_student_assoc_mock(student_id=10, school_id=1)
        student2 = _make_student_assoc_mock(student_id=11, school_id=2)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[school1, school2],
            ),
            patch("app.infrastructure.school.repository.SQLAlchemySchoolRepository"),
        ):
            mock_cu.students = [student1, student2]
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_calendar")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /management_earlycare_calendar (lines 63-83)
# ---------------------------------------------------------------------------


class TestManagementEarlycareCalendarGet:
    def test_requires_login(self, client):
        """GET /management_earlycare_calendar sin sesión → 302."""
        response = client.get("/management_earlycare_calendar", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_one_school_renders_earlycare_calendar(self, client, app, db):
        """GET /management_earlycare_calendar con 1 escuela → earlycare_calendar.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school_mock = _make_school_mock(school_id=5)
        school_assoc = MagicMock()
        school_assoc.school_id = 5

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[school_mock],
            ),
            patch(
                "app.infrastructure.school.repository.SQLAlchemySchoolRepository.get_by_id",
                return_value=school_mock,
            ),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_start_date_early_lunch",
                return_value="2026-01-15",
            ),
            patch("app.adapters.views.calendar_station_routes.get_calendar_events", return_value=[]),
        ):
            mock_cu.schools = [school_assoc]
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_earlycare_calendar")

        assert response.status_code == 200

    def test_zero_schools_renders_calendar_list(self, client, app, db):
        """GET /management_earlycare_calendar con 0 escuelas → calendar_list.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[],
            ),
            patch("app.infrastructure.school.repository.SQLAlchemySchoolRepository"),
        ):
            mock_cu.schools = []
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_earlycare_calendar")

        assert response.status_code == 200

    def test_two_schools_renders_calendar_list(self, client, app, db):
        """GET /management_earlycare_calendar con 2 escuelas → calendar_list.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school1 = _make_school_mock(school_id=5)
        school2 = _make_school_mock(school_id=6)
        assoc1 = MagicMock()
        assoc1.school_id = 5
        assoc2 = MagicMock()
        assoc2.school_id = 6

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[school1, school2],
            ),
            patch("app.infrastructure.school.repository.SQLAlchemySchoolRepository"),
        ):
            mock_cu.schools = [assoc1, assoc2]
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_earlycare_calendar")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /management_earlycare_calendar (lines 89-96)
# ---------------------------------------------------------------------------


class TestManagementEarlycareCalendarPost:
    def test_requires_login(self, client):
        """POST /management_earlycare_calendar sin sesión → 302."""
        response = client.post(
            "/management_earlycare_calendar",
            data={"centerId": "1"},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_with_center_id_renders_calendar(self, client, app, db):
        """POST /management_earlycare_calendar con centerId → calendar.html (200)."""
        from tests.factories.school_orm_factory import SchoolORMFactory
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            SchoolORMFactory._meta.sqlalchemy_session = db.session
            school = SchoolORMFactory.create(status=1)
            school_id = school.id
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school_mock = _make_school_mock(school_id=school_id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.infrastructure.school.repository.SQLAlchemySchoolRepository.get_by_id",
                return_value=school_mock,
            ),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_start_date_early_lunch",
                return_value="2026-01-15",
            ),
            patch("app.adapters.views.calendar_station_routes.get_calendar_events", return_value=[]),
        ):
            mock_cu.is_authenticated = True
            mock_cu.students = []

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/management_earlycare_calendar",
                    data={"centerId": str(school_id)},
                )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /management_lunchcare_calendar (lines 108-128)
# ---------------------------------------------------------------------------


class TestManagementLunchcareCalendarGet:
    def test_requires_login(self, client):
        """GET /management_lunchcare_calendar sin sesión → 302."""
        response = client.get("/management_lunchcare_calendar", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_one_school_renders_lunchcare_calendar(self, client, app, db):
        """GET /management_lunchcare_calendar con 1 escuela → lunchcare_calendar.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school_mock = _make_school_mock(school_id=7)
        school_assoc = MagicMock()
        school_assoc.school_id = 7

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[school_mock],
            ),
            patch(
                "app.infrastructure.school.repository.SQLAlchemySchoolRepository.get_by_id",
                return_value=school_mock,
            ),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_start_date_early_lunch",
                return_value="2026-01-15",
            ),
            patch("app.adapters.views.calendar_station_routes.get_calendar_events", return_value=[]),
        ):
            mock_cu.schools = [school_assoc]
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_lunchcare_calendar")

        assert response.status_code == 200

    def test_zero_schools_renders_calendar_list(self, client, app, db):
        """GET /management_lunchcare_calendar con 0 escuelas → calendar_list.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[],
            ),
            patch("app.infrastructure.school.repository.SQLAlchemySchoolRepository"),
        ):
            mock_cu.schools = []
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_lunchcare_calendar")

        assert response.status_code == 200

    def test_two_schools_renders_calendar_list(self, client, app, db):
        """GET /management_lunchcare_calendar con 2 escuelas → calendar_list.html (200)."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school1 = _make_school_mock(school_id=7)
        school2 = _make_school_mock(school_id=8)
        assoc1 = MagicMock()
        assoc1.school_id = 7
        assoc2 = MagicMock()
        assoc2.school_id = 8

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.school.get_schools_by_ids.GetSchoolsByIdsUseCase.execute",
                return_value=[school1, school2],
            ),
            patch("app.infrastructure.school.repository.SQLAlchemySchoolRepository"),
        ):
            mock_cu.schools = [assoc1, assoc2]
            mock_cu.is_authenticated = True

            _setup_session(client, user_id)
            with app.app_context():
                response = client.get("/management_lunchcare_calendar")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /management_lunchcare_calendar (lines 134-141)
# ---------------------------------------------------------------------------


class TestManagementLunchcareCalendarPost:
    def test_requires_login(self, client):
        """POST /management_lunchcare_calendar sin sesión → 302."""
        response = client.post(
            "/management_lunchcare_calendar",
            data={"centerId": "1"},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_with_center_id_renders_calendar(self, client, app, db):
        """POST /management_lunchcare_calendar con centerId → calendar.html (200)."""
        from tests.factories.school_orm_factory import SchoolORMFactory
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            SchoolORMFactory._meta.sqlalchemy_session = db.session
            school = SchoolORMFactory.create(status=1)
            school_id = school.id
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school_mock = _make_school_mock(school_id=school_id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.infrastructure.school.repository.SQLAlchemySchoolRepository.get_by_id",
                return_value=school_mock,
            ),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_start_date_early_lunch",
                return_value="2026-01-15",
            ),
            patch("app.adapters.views.calendar_station_routes.get_calendar_events", return_value=[]),
        ):
            mock_cu.is_authenticated = True
            mock_cu.students = []

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/management_lunchcare_calendar",
                    data={"centerId": str(school_id)},
                )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /management_calendar (lines 153-160)
# ---------------------------------------------------------------------------


class TestManagementCalendarPost:
    def test_requires_login(self, client):
        """POST /management_calendar sin sesión → 302."""
        response = client.post(
            "/management_calendar",
            data={"centerId": "1"},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_with_center_id_renders_calendar(self, client, app, db):
        """POST /management_calendar con centerId → calendar.html (200)."""
        from tests.factories.school_orm_factory import SchoolORMFactory
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            SchoolORMFactory._meta.sqlalchemy_session = db.session
            school = SchoolORMFactory.create(status=1)
            school_id = school.id
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school_mock = _make_school_mock(school_id=school_id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.infrastructure.school.repository.SQLAlchemySchoolRepository.get_by_id",
                return_value=school_mock,
            ),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_start_date",
                return_value="2026-01-15",
            ),
            patch("app.adapters.views.calendar_station_routes.get_calendar_events", return_value=[]),
        ):
            mock_cu.is_authenticated = True
            mock_cu.students = []

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/management_calendar",
                    data={"centerId": str(school_id)},
                )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /save_calendar_event (lines 231-297)
# ---------------------------------------------------------------------------


class TestSaveCalendarEvent:
    def test_requires_login(self, client):
        """POST /save_calendar_event sin sesión → 302."""
        response = client.post(
            "/save_calendar_event",
            json={
                "current_from_date": "01/01/2026",
                "current_to_date": "07/01/2026",
                "current_early_request": {},
                "current_early_plus_request": {},
                "current_lunch_request": {},
            },
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_with_valid_dates_returns_json(self, client, app, db):
        """POST /save_calendar_event con fechas y datos → 200 + JSON con event_dates."""
        from datetime import date

        from app.application.attendance.save_attendance_range import SaveAttendanceRangeResult
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        student_assoc = _make_student_assoc_mock(student_id=42, school_id=3)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.attendance.save_attendance_range.SaveAttendanceRangeUseCase.execute",
                return_value=SaveAttendanceRangeResult(
                    saved_dates=[date(2026, 1, 5)],
                    skipped_dates=[date(2026, 1, 6)],
                ),
            ),
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.holyday.repository.SQLAlchemyHolydayRepository"),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_events",
                return_value=[
                    ("2026-01-05", "early", "20260105"),
                ],
            ),
        ):
            mock_cu.is_authenticated = True
            mock_cu.students = [student_assoc]

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/save_calendar_event",
                    json={
                        "current_from_date": "01/01/2026",
                        "current_to_date": "07/01/2026",
                        "current_early_request": {"42": 1},
                        "current_early_plus_request": {"42": 0},
                        "current_lunch_request": {"42": 0},
                    },
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "event_dates" in data
        assert "saved_dates" in data
        assert "skipped_dates" in data
        assert "event_type" in data

    def test_post_with_empty_attendance_returns_empty_event_dates(self, client, app, db):
        """POST /save_calendar_event sin asistencias → 200 + event_dates vacío."""
        from datetime import date

        from app.application.attendance.save_attendance_range import SaveAttendanceRangeResult
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.attendance.save_attendance_range.SaveAttendanceRangeUseCase.execute",
                return_value=SaveAttendanceRangeResult(
                    saved_dates=[],
                    skipped_dates=[],
                ),
            ),
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.holyday.repository.SQLAlchemyHolydayRepository"),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_events",
                return_value=[],
            ),
        ):
            mock_cu.is_authenticated = True
            mock_cu.students = []

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/save_calendar_event",
                    json={
                        "current_from_date": "01/01/2026",
                        "current_to_date": "07/01/2026",
                        "current_early_request": {},
                        "current_early_plus_request": {},
                        "current_lunch_request": {},
                    },
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert data["event_dates"] == []
        assert data["saved_dates"] == []
        assert data["skipped_dates"] == []

    def test_post_saved_dates_not_in_events_get_null_event_type(self, client, app, db):
        """POST /save_calendar_event: fechas guardadas sin eventos → event_type=null."""
        from datetime import date

        from app.application.attendance.save_attendance_range import SaveAttendanceRangeResult
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        student_assoc = _make_student_assoc_mock(student_id=55, school_id=4)

        with (
            patch("app.adapters.views.calendar_station_routes.current_user") as mock_cu,
            patch(
                "app.application.attendance.save_attendance_range.SaveAttendanceRangeUseCase.execute",
                return_value=SaveAttendanceRangeResult(
                    saved_dates=[date(2026, 1, 10)],
                    skipped_dates=[],
                ),
            ),
            patch("app.infrastructure.attendance.repository.SQLAlchemyEarlyRepository"),
            patch("app.infrastructure.attendance.repository.SQLAlchemyLunchRepository"),
            patch("app.infrastructure.holyday.repository.SQLAlchemyHolydayRepository"),
            patch(
                "app.adapters.views.calendar_station_routes.get_calendar_events",
                return_value=[],  # No events → saved dates have no event type
            ),
        ):
            mock_cu.is_authenticated = True
            mock_cu.students = [student_assoc]

            _setup_session(client, user_id)
            with app.app_context():
                response = client.post(
                    "/save_calendar_event",
                    json={
                        "current_from_date": "10/01/2026",
                        "current_to_date": "10/01/2026",
                        "current_early_request": {"55": 1},
                        "current_early_plus_request": {},
                        "current_lunch_request": {},
                    },
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert len(data["event_dates"]) == 1
        assert data["event_dates"][0]["event_type"] is None
        assert data["event_dates"][0]["start"] == "2026-01-10"
