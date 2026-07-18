"""
Tests HTTP para school_routes (Blueprint school_bp, prefix /management/schools).

REQ-V01 + REQ-V02.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.school.edit import SchoolNotFoundError
from tests.factories.school_factory import SchoolFactory

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


class TestSchoolRoutesAuth:
    def test_list_schools_requires_login(self, client):
        """GET /management/schools/ sin sesión → redirect a login."""
        response = client.get("/management/schools/", follow_redirects=False)
        assert response.status_code in (301, 302)


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------


class TestSchoolRoutesCRUD:
    def test_list_schools_returns_200(self, client, app, db):
        """GET /management/schools/ con admin logueado → 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        schools = [SchoolFactory.build(status=1)]

        with patch("app.adapters.views.school_routes.ListSchoolsUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = schools
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/schools/")

        assert response.status_code == 200

    def test_create_school_post_redirects(self, client, app, db):
        """POST /management/schools/ → redirect después de crear."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.school_routes.CreateSchoolUseCase") as mock_uc:
            saved = SchoolFactory.build()
            mock_uc.return_value.execute.return_value = saved
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/schools/",
                        data={
                            "centerName": "Colexio Test",
                            "centerAddress": "Rúa Test",
                            "centerPhone": "",
                            "centerMail": "",
                        },
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)

    def test_get_school_json_returns_200(self, client, app, db):
        """GET /management/schools/<id> → JSON 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        school = SchoolFactory.build(id=42, name="Colexio JSON")

        with patch("app.adapters.views.school_routes.GetSchoolUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = school
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/schools/42")

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Colexio JSON"

    def test_delete_school_soft_deletes(self, client, app, db):
        """POST /management/schools/<id>/delete → redirect."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.school_routes.DeleteSchoolUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = None
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post("/management/schools/42/delete", follow_redirects=False)

        assert response.status_code in (301, 302)
