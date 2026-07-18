"""
Tests HTTP para holyday_routes (Blueprint holyday_bp, prefix /management/holydays).

REQ-V01 + REQ-V02.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.application.holyday.get import HolydayNotFoundError
from tests.factories.holyday_factory import HolydayFactory

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


class TestHolydayRoutesAuth:
    def test_list_holydays_requires_login(self, client):
        """GET /management/holydays/ sin sesión → redirect a login."""
        response = client.get("/management/holydays/", follow_redirects=False)
        assert response.status_code in (301, 302)


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------


class TestHolydayRoutesCRUD:
    def test_list_holydays_returns_200(self, client, app, db):
        """GET /management/holydays/ con admin logueado → 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        holydays = [HolydayFactory.build(status=1)]

        with patch("app.adapters.views.holyday_routes.ListHolydaysUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = holydays
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/holydays/")

        assert response.status_code == 200

    def test_create_holyday_post_redirects(self, client, app, db):
        """POST /management/holydays/ → redirect después de crear."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.holyday_routes.CreateHolydayUseCase") as mock_uc:
            saved = HolydayFactory.build()
            mock_uc.return_value.execute.return_value = saved
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/holydays/",
                        data={
                            "dataHolydayDateValue": "01/06/2026",
                        },
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)

    def test_get_holyday_json_returns_200(self, client, app, db):
        """GET /management/holydays/<id> → JSON 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        holyday = HolydayFactory.build(id=42, holyday=date(2026, 6, 1))

        with patch("app.adapters.views.holyday_routes.GetHolydayUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = holyday
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/holydays/42")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == 42

    def test_edit_holyday_post_redirects(self, client, app, db):
        """POST /management/holydays/<id> → redirect después de editar."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.holyday_routes.EditHolydayUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = HolydayFactory.build()
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/holydays/42",
                        data={
                            "dataHolydayDateValue": "04/07/2026",
                        },
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)

    def test_delete_holyday_soft_deletes(self, client, app, db):
        """POST /management/holydays/<id>/delete → redirect."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.holyday_routes.DeleteHolydayUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = None
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post("/management/holydays/42/delete", follow_redirects=False)

        assert response.status_code in (301, 302)
