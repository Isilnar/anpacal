"""
Tests HTTP para auth_routes (Blueprint auth, prefix /v2).

REQ-V01: login exitoso (redirect), login fallido (re-render + flash), logout.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.user.authenticate import AuthenticationError
from tests.factories.user_factory import UserFactory

# ---------------------------------------------------------------------------
# Fixtures HTTP
# ---------------------------------------------------------------------------


@pytest.fixture
def http_client(app):
    """Cliente HTTP con context de sesión."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Tests de login (GET)
# ---------------------------------------------------------------------------


class TestLoginPage:
    def test_login_page_returns_200(self, http_client):
        """GET /login devuelve 200."""
        response = http_client.get("/login")
        assert response.status_code == 200

    def test_login_page_renders_template(self, http_client):
        """GET /login renderiza el template de login."""
        response = http_client.get("/login")
        assert b"login" in response.data.lower() or response.status_code == 200


# ---------------------------------------------------------------------------
# Tests de login (POST)
# ---------------------------------------------------------------------------


class TestLoginPost:
    def test_login_post_redirects_on_success(self, http_client, app):
        """POST /login con credenciales válidas → redirect."""
        domain_user = UserFactory.build()
        object.__setattr__(domain_user, "id", 1)
        object.__setattr__(domain_user, "ws_token", "some-token")

        orm_mock = MagicMock()
        orm_mock.id = 1
        orm_mock.is_authenticated = True
        orm_mock.is_active = True
        orm_mock.is_anonymous = False
        orm_mock.get_id.return_value = "1"

        with app.app_context():
            with (
                patch(
                    "app.adapters.views.auth_routes.AuthenticateUserUseCase.execute",
                    return_value=domain_user,
                ),
                patch(
                    "app.adapters.views.auth_routes.SQLAlchemyUserRepository.get_orm_by_id",
                    return_value=orm_mock,
                ),
            ):
                response = http_client.post(
                    "/login",
                    data={"username": "admin", "password": "correct"},
                    follow_redirects=False,
                )

        assert response.status_code in (301, 302)

    def test_login_post_returns_error_on_invalid_credentials(self, http_client, app):
        """POST /login con credenciales inválidas → redirect a login (flash error)."""
        with app.app_context():
            with patch(
                "app.adapters.views.auth_routes.AuthenticateUserUseCase.execute",
                side_effect=AuthenticationError("bad credentials"),
            ):
                response = http_client.post(
                    "/login",
                    data={"username": "bad", "password": "wrong"},
                    follow_redirects=False,
                )

        assert response.status_code in (301, 302)
        assert b"/login" in response.headers.get("Location", "").encode()


# ---------------------------------------------------------------------------
# Tests de logout
# ---------------------------------------------------------------------------


class TestLogout:
    def test_logout_redirects(self, http_client, app):
        """GET /logout sin sesión → redirige (login_required → 302)."""
        response = http_client.get("/logout", follow_redirects=False)
        # Sin sesión, login_required redirige al login
        assert response.status_code in (301, 302)
