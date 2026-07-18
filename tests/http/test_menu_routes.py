"""
Tests HTTP para menu_routes (Blueprint menu_bp, prefix /management/menu).

REQ-V01 + REQ-V02.
Regla: mock_cu.is_admin = lambda: 1  (NO .return_value)
"""

from unittest.mock import MagicMock, patch

import pytest

from tests.factories.menu_factory import MenuFactory

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


class TestMenuRoutesAuth:
    def test_get_menu_requires_login(self, client):
        """GET /management/menu/ sin sesión → redirect a login."""
        response = client.get("/management/menu/", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_post_menu_requires_login(self, client):
        """POST /management/menu/ sin sesión → redirect a login."""
        response = client.post("/management/menu/", follow_redirects=False)
        assert response.status_code in (301, 302)


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------


class TestMenuRoutes:
    def test_get_menu_returns_200(self, client, app, db):
        """GET /management/menu/ con admin logueado → 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        menu = MenuFactory.build(menu_link="/static/menu.json", status=1)

        with patch("app.adapters.views.menu_routes.GetActiveMenuUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = menu
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/menu/")

        assert response.status_code == 200

    def test_get_menu_no_active_returns_200(self, client, app, db):
        """GET /management/menu/ sin menú activo → 200 con menu_link vacío."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.menu_routes.GetActiveMenuUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = None
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/menu/")

        assert response.status_code == 200

    def test_post_menu_sets_active_and_renders(self, client, app, db):
        """POST /management/menu/ → SetMenuUseCase llamado, retorna 200."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        saved = MenuFactory.build(menu_link="/posted_menu.json", status=1)

        with patch("app.adapters.views.menu_routes.SetMenuUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = saved
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/menu/",
                        data={
                            "menu_link": "/posted_menu.json",
                        },
                    )

        assert response.status_code == 200

    def test_post_menu_calls_use_case_with_link(self, client, app, db):
        """POST verifica que SetMenuUseCase.execute recibe el menu_link correcto."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        saved = MenuFactory.build(menu_link="/correct_link.json", status=1)

        with patch("app.adapters.views.menu_routes.SetMenuUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = saved
            _setup_session(client, user_id)

            with patch("app.adapters.decorators.current_user", is_admin=lambda: 1, is_family=lambda: 0) as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    client.post(
                        "/management/menu/",
                        data={
                            "menu_link": "/correct_link.json",
                        },
                    )

        mock_uc.return_value.execute.assert_called_once_with("/correct_link.json")
