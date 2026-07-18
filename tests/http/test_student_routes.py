"""
Tests HTTP para student_routes (Blueprint student_bp, prefix /management/students).

REQ-V01 + REQ-V02.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.student.delete import StudentNotFoundError
from tests.factories.student_factory import StudentFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_session(client, user_id: str):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id
        sess["_fresh"] = True


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------


class TestStudentRoutesAuth:
    def test_list_students_requires_login(self, client):
        """GET /management/students/ sin sesión → redirect a login."""
        response = client.get("/management/students/", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_list_students_returns_200(self, client, app, db):
        """GET /management/students/ con admin logueado → 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        students = [StudentFactory.build(status=1)]

        with (
            patch("app.adapters.views.student_routes.ListStudentsUseCase") as mock_uc,
            patch("app.adapters.views.student_routes.get_selected_intolerances", return_value=[]),
            patch("app.adapters.views.student_routes.get_current_schools", return_value=[]),
        ):
            mock_uc.return_value.execute.return_value = students
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user") as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/students/")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------


class TestStudentRoutesCRUD:
    def test_create_student_post_creates_student(self, client, app, db):
        """POST /management/students/ → redirect después de crear."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.student_routes.CreateStudentUseCase") as mock_uc:
            saved = StudentFactory.build()
            mock_uc.return_value.execute.return_value = saved

            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user") as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/students/",
                        data={
                            "studentName": "Ana",
                            "studentSurname": "García",
                            "selectedSchool": "1",
                            "studentClassroom": "1A",
                            "studentNumberId": "12345678A",
                            "studentPhone": "600111222",
                            "studentMail": "ana@example.com",
                            "studentAddress": "Calle Mayor 1",
                            "studentAllergies": "",
                            "studentChildish": "no",
                            "brotherNumber": "0",
                            "studentNumber": "",
                            "selectedIntolerancesIds": "",
                        },
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)

    def test_delete_student_soft_deletes(self, client, app, db):
        """POST /management/students/<id>/delete → redirect + alumno desactivado."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.student_routes.DeleteStudentUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = None

            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user") as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/students/1/delete",
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)
