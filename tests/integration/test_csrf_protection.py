"""
test_csrf_protection.py — Verify CSRF tokens are required on POST endpoints.

These tests run with WTF_CSRF_ENABLED=True (unlike the rest of the test suite)
to catch forms that forget to include the CSRF token.
"""

import pytest

from app import create_app
from app import db as _db

CSRF_TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SECRET_KEY": "csrf-test-secret-key",
    "FERNET_KEY": "6TiOB1atiuV0uAS2EiR6x0iqxW4qO8d-sf2nZltF1L4=",
    "WTF_CSRF_ENABLED": True,  # CSRF active — the whole point of this test
    "WTF_CSRF_SSL_STRICT": False,
    "RATELIMIT_ENABLED": False,
    "MAIL_SERVER": "localhost",
    "MAIL_PORT": 25,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": "",
    "MAIL_PASSWORD": "",
    "MAIL_RESPONSE_ADDRESS": "",
}


@pytest.fixture(scope="module")
def csrf_app():
    """Flask app with CSRF protection enabled."""
    app = create_app(test_config=CSRF_TEST_CONFIG)
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()


@pytest.fixture(scope="module")
def csrf_db(csrf_app):
    with csrf_app.app_context():
        yield _db


@pytest.fixture()
def csrf_client(csrf_app):
    return csrf_app.test_client()


def _login_admin(csrf_client, csrf_app, csrf_db):
    """Create admin user and log in, returning the client with active session."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with csrf_app.app_context():
        role = csrf_db.session.query(Role).filter_by(name="admin").first()
        if not role:
            role = Role(name="admin", description="Administrador")
            csrf_db.session.add(role)
            csrf_db.session.flush()

        user = csrf_db.session.query(User).filter_by(username="csrf_admin").first()
        if not user:
            user = User(
                username="csrf_admin",
                password=bcrypt.generate_password_hash("csrf_pass").decode("utf-8"),
                name="CSRF",
                surname="Admin",
                status=1,
                ws_token="csrf-token-123",
            )
            csrf_db.session.add(user)
            csrf_db.session.flush()
            csrf_db.session.add(UserRoleAssociation(user_id=user.id, role_id=role.id))
            csrf_db.session.commit()

        user_id = csrf_db.session.query(User).filter_by(username="csrf_admin").first().id

    # Login via session injection
    with csrf_client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)


def _get_csrf_token(csrf_client, url):
    """Fetch a page and extract the CSRF token from the meta tag or hidden input."""
    response = csrf_client.get(url)
    html = response.data.decode()

    # Try meta tag first (layout.html has <meta name="csrf-token" content="...">)
    import re

    match = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
    if match:
        return match.group(1)

    # Try hidden input
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if match:
        return match.group(1)

    raise ValueError(f"CSRF token not found in response from {url}")


class TestCsrfMenuRoute:
    """POST /management/menu/ must include CSRF token."""

    def test_post_without_csrf_returns_400(self, csrf_client, csrf_app, csrf_db):
        """POST without CSRF token is rejected with 400."""
        _login_admin(csrf_client, csrf_app, csrf_db)
        response = csrf_client.post(
            "/management/menu/",
            data={"menu_link": "https://example.com/menu.pdf"},
        )
        assert response.status_code == 400

    def test_post_with_csrf_succeeds(self, csrf_client, csrf_app, csrf_db):
        """POST with valid CSRF token succeeds (200)."""
        _login_admin(csrf_client, csrf_app, csrf_db)
        token = _get_csrf_token(csrf_client, "/management/menu/")
        response = csrf_client.post(
            "/management/menu/",
            data={"menu_link": "https://example.com/menu.pdf", "csrf_token": token},
        )
        assert response.status_code == 200


class TestCsrfLoginRoute:
    """POST /login must include CSRF token."""

    def test_login_without_csrf_returns_400(self, csrf_client, csrf_app, csrf_db):
        """POST /login without CSRF token is rejected."""
        response = csrf_client.post(
            "/login",
            data={"username": "someone", "password": "something"},
        )
        assert response.status_code == 400

    def test_login_with_csrf_processes_request(self):
        """POST /login with CSRF token is processed (302 redirect on bad creds)."""
        import re

        from app import create_app
        from app import db as app_db

        # Isolated app + client to avoid session pollution from module-scoped fixtures
        app = create_app(test_config=CSRF_TEST_CONFIG)
        with app.app_context():
            app_db.create_all()

        with app.test_client() as client:
            # GET login page seeds session with csrf_token
            get_resp = client.get("/login")
            assert get_resp.status_code == 200
            html = get_resp.data.decode()

            match = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
            assert match, "CSRF meta tag must be present"
            token = match.group(1)

            # POST with valid CSRF token — should be processed (not 400)
            response = client.post(
                "/login",
                data={"username": "nonexistent", "password": "wrong", "csrf_token": token},
                follow_redirects=False,
            )
            # Bad credentials → redirect back to login (302), not CSRF error (400)
            assert response.status_code == 302


class TestCsrfReportsRoute:
    """POST /management/reports/create must include CSRF token."""

    def test_reports_without_csrf_returns_400(self, csrf_client, csrf_app, csrf_db):
        """POST without CSRF token is rejected."""
        _login_admin(csrf_client, csrf_app, csrf_db)
        response = csrf_client.post(
            "/management/reports/create",
            data={"reportType": "1", "validFrom": "01/01/2025", "validUntil": "31/01/2025", "student": ""},
        )
        assert response.status_code == 400
