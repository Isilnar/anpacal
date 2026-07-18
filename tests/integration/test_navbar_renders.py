"""
Tests de integración: navbar se renderiza con los enlaces correctos por rol.

Verifica que cada tipo de usuario (admin, lunchcare, earlycare, family) vea
los enlaces correspondientes en el menú superior y NO vea los de otros roles.

Esto cubre el bug anterior donde lunchcare no veía "Xeración de informes"
y el calendario siempre apuntaba al general.
"""

import pytest

# ---------------------------------------------------------------------------
# Helpers — crear usuarios por rol y login
# ---------------------------------------------------------------------------


def _create_role(app, db, name, description):
    """Crea un rol si no existe. Devuelve el objeto RoleORM."""
    from app.infrastructure.role.orm import RoleORM as Role

    role = db.session.query(Role).filter_by(name=name).first()
    if not role:
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.flush()
    return role


def _create_user(app, db, username, password, role_name, role_desc):
    """Crea usuario con un rol y lo asocia. Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    user = db.session.query(User).filter_by(username=username).first()
    if not user:
        role = _create_role(app, db, role_name, role_desc)
        user = User(
            username=username,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            name=role_name.title(),
            surname="Test",
            status=1,
            ws_token=f"token-{username}",
        )
        db.session.add(user)
        db.session.flush()
        assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
        db.session.add(assoc)
        db.session.commit()
    return username, password


def _login(client, username, password):
    """Hace POST /login para autenticar al cliente."""
    client.post("/login", data={"username": username, "password": password})


# ---------------------------------------------------------------------------
# Fixtures de usuarios por rol (session-scoped para eficiencia)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def admin_creds(app, db):
    with app.app_context():
        return _create_user(app, db, "nav_admin", "pass", "admin", "Administrador")


@pytest.fixture(scope="module")
def lunchcare_creds(app, db):
    with app.app_context():
        return _create_user(app, db, "nav_lunch", "pass", "lunchcare", "Comedor")


@pytest.fixture(scope="module")
def earlycare_creds(app, db):
    with app.app_context():
        return _create_user(app, db, "nav_early", "pass", "earlycare", "Madrugadores")


@pytest.fixture(scope="module")
def family_creds(app, db):
    with app.app_context():
        return _create_user(app, db, "nav_family", "pass", "family", "Familiar")


# ---------------------------------------------------------------------------
# Tests — admin
# ---------------------------------------------------------------------------


class TestNavbarAsAdmin:
    def test_admin_sees_schools_students_users_reports_registers_holydays_menu(self, client, app, db, admin_creds):
        _login(client, *admin_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        # Admin links que DEBEN aparecer
        assert 'id="nav-link-manage-schools"' in body
        assert 'id="nav-link-manage-students"' in body
        assert 'id="nav-link-manage-users"' in body
        assert 'id="nav-link-manage-reports"' in body
        assert 'id="nav-link-manage-registers"' in body
        assert 'id="nav-link-manage-holydays"' in body
        assert 'id="nav-link-manage-menu"' in body

    def test_admin_does_not_see_role_specific_calendars(self, client, app, db, admin_creds):
        _login(client, *admin_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        # Admin NO debe ver calendarios específicos de rol
        assert 'id="nav-link-manage-lunchcare-calendar"' not in body
        assert 'id="nav-link-manage-earlycare-calendar"' not in body

    def test_admin_does_not_see_role_reports(self, client, app, db, admin_creds):
        _login(client, *admin_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-manage-lunchcare-reports"' not in body
        assert 'id="nav-link-manage-earlycare-reports"' not in body


# ---------------------------------------------------------------------------
# Tests — lunchcare (comedor)
# ---------------------------------------------------------------------------


class TestNavbarAsLunchcare:
    def test_lunchcare_sees_menu_and_password(self, client, app, db, lunchcare_creds):
        _login(client, *lunchcare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-menu"' in body
        assert 'id="nav-link-manage-password"' in body

    def test_lunchcare_sees_calendar_and_reports_links(self, client, app, db, lunchcare_creds):
        _login(client, *lunchcare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        # Enlaces específicos de comedor
        assert 'id="nav-link-manage-lunchcare-calendar"' in body
        assert 'id="nav-link-manage-lunchcare-reports"' in body

    def test_lunchcare_does_not_see_earlycare_or_admin_links(self, client, app, db, lunchcare_creds):
        _login(client, *lunchcare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-manage-earlycare-calendar"' not in body
        assert 'id="nav-link-manage-earlycare-reports"' not in body
        assert 'id="nav-link-manage-schools"' not in body
        assert 'id="nav-link-manage-students"' not in body

    def test_lunchcare_calendar_links_to_lunchcare_endpoint(self, client, app, db, lunchcare_creds):
        """El enlace del calendario debe apuntar a management_lunchcare_calendar."""
        _login(client, *lunchcare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert "/management_lunchcare_calendar" in body

    def test_lunchcare_reports_links_to_lunchcare_reports(self, client, app, db, lunchcare_creds):
        """El enlace de informes debe apuntar a /management/lunchcare-reports/."""
        _login(client, *lunchcare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert "/management/lunchcare-reports/" in body


# ---------------------------------------------------------------------------
# Tests — earlycare (madrugadores)
# ---------------------------------------------------------------------------


class TestNavbarAsEarlycare:
    def test_earlycare_sees_menu_and_password(self, client, app, db, earlycare_creds):
        _login(client, *earlycare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-menu"' in body
        assert 'id="nav-link-manage-password"' in body

    def test_earlycare_sees_calendar_and_reports_links(self, client, app, db, earlycare_creds):
        _login(client, *earlycare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-manage-earlycare-calendar"' in body
        assert 'id="nav-link-manage-earlycare-reports"' in body

    def test_earlycare_does_not_see_lunchcare_or_admin_links(self, client, app, db, earlycare_creds):
        _login(client, *earlycare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-manage-lunchcare-calendar"' not in body
        assert 'id="nav-link-manage-lunchcare-reports"' not in body
        assert 'id="nav-link-manage-schools"' not in body
        assert 'id="nav-link-manage-students"' not in body

    def test_earlycare_calendar_links_to_earlycare_endpoint(self, client, app, db, earlycare_creds):
        _login(client, *earlycare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert "/management_earlycare_calendar" in body

    def test_earlycare_reports_links_to_earlycare_reports(self, client, app, db, earlycare_creds):
        _login(client, *earlycare_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert "/management/earlycare-reports/" in body


# ---------------------------------------------------------------------------
# Tests — family
# ---------------------------------------------------------------------------


class TestNavbarAsFamily:
    def test_family_sees_menu_and_password(self, client, app, db, family_creds):
        _login(client, *family_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-menu"' in body
        assert 'id="nav-link-manage-password"' in body

    def test_family_sees_general_calendar(self, client, app, db, family_creds):
        """Family ve el calendario escolar general."""
        _login(client, *family_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-manage-calendar"' in body

    def test_family_does_not_see_role_specific_calendars_or_reports(self, client, app, db, family_creds):
        _login(client, *family_creds)
        resp = client.get("/")
        body = resp.data.decode("utf-8")

        assert 'id="nav-link-manage-lunchcare-calendar"' not in body
        assert 'id="nav-link-manage-earlycare-calendar"' not in body
        assert 'id="nav-link-manage-lunchcare-reports"' not in body
        assert 'id="nav-link-manage-earlycare-reports"' not in body
        assert 'id="nav-link-manage-schools"' not in body
