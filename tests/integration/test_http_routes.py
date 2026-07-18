"""
test_http_routes.py — Tests HTTP para TODAS las rutas de entidades no cubiertas en
test_http_contracts.py.

Verifica:
  1. Sin autenticación → 302 a /login
  2. Con autenticación admin → 200 (GETs de página) o 200/302 (POSTs)
  3. Para endpoints JSON específicos → status_code == 200 y JSON válido

NOTA DE IMPLEMENTACIÓN — aislamiento de sesión Flask-Login:
  Flask-Login almacena el usuario cargado en `g._login_user`. En Flask 3.x, `g`
  está ligado al app context (no al request context). El fixture `db` (scope=session)
  mantiene el app context vivo durante toda la sesión de tests. Esto significa que
  `g._login_user` persiste entre tests si no se limpia explícitamente.
  La función `_clear_login_state(app)` limpia este estado antes de cada test
  que debe ejecutarse como usuario no autenticado.
"""

import pytest
from flask import g

from tests.factories.holyday_orm_factory import HolydayORMFactory
from tests.factories.menu_orm_factory import MenuORMFactory
from tests.factories.school_orm_factory import SchoolORMFactory
from tests.factories.student_orm_factory import StudentORMFactory
from tests.factories.user_orm_factory import UserORMFactory

# ---------------------------------------------------------------------------
# Helpers — aislamiento de sesión y creación idempotente de usuarios
# ---------------------------------------------------------------------------


def _clear_login_state(app):
    """Limpia el usuario cacheado en g para simular acceso sin autenticar.

    Flask-Login guarda el usuario en g._login_user dentro del app context.
    Como el app context (del fixture `db`) persiste entre tests, este estado
    debe limpiarse explícitamente antes de tests que verifican comportamiento
    sin autenticación.

    NOTA: NO usar `with app.app_context()` aquí porque crea un context ANIDADO
    con su propio `g`. Accedemos directamente al `g` del context actual.
    """
    # Accede al app context activo (el del fixture `db`, scope=session)
    # y limpia el _login_user cacheado por Flask-Login en dicho contexto.
    from flask.globals import _cv_app

    ctx = _cv_app.get(None)
    if ctx is not None:
        local_g = ctx.g
        if hasattr(local_g, "_login_user"):
            delattr(local_g, "_login_user")


def _get_or_create_admin(app, db):
    """Crea un usuario admin (idempotente). Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        user = db.session.query(User).filter_by(username="routes_admin").first()
        if not user:
            role = db.session.query(Role).filter_by(name="admin").first()
            if not role:
                role = Role(name="admin", description="Administrador")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="routes_admin",
                password=bcrypt.generate_password_hash("routes_pass").decode("utf-8"),
                name="Routes",
                surname="Admin",
                status=1,
                ws_token="routes-admin-token",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    return "routes_admin", "routes_pass"


def _get_or_create_earlycare_user(app, db):
    """Crea un usuario con rol earlycare (idempotente). Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        user = db.session.query(User).filter_by(username="routes_earlycare").first()
        if not user:
            role = db.session.query(Role).filter_by(name="earlycare").first()
            if not role:
                role = Role(name="earlycare", description="Madrugadores")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="routes_earlycare",
                password=bcrypt.generate_password_hash("earlycare_pass").decode("utf-8"),
                name="Early",
                surname="Care",
                status=1,
                ws_token="routes-earlycare-token",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    return "routes_earlycare", "earlycare_pass"


def _get_or_create_lunchcare_user(app, db):
    """Crea un usuario con rol lunchcare (idempotente). Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        user = db.session.query(User).filter_by(username="routes_lunchcare").first()
        if not user:
            role = db.session.query(Role).filter_by(name="lunchcare").first()
            if not role:
                role = Role(name="lunchcare", description="Comedor")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="routes_lunchcare",
                password=bcrypt.generate_password_hash("lunchcare_pass").decode("utf-8"),
                name="Lunch",
                surname="Care",
                status=1,
                ws_token="routes-lunchcare-token",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    return "routes_lunchcare", "lunchcare_pass"


def _login(client, username, password):
    """Envía POST /login con las credenciales dadas."""
    client.post("/login", data={"username": username, "password": password})


def _login_admin(client, app, db):
    username, password = _get_or_create_admin(app, db)
    _login(client, username, password)


def _login_earlycare(client, app, db):
    username, password = _get_or_create_earlycare_user(app, db)
    _login(client, username, password)


def _login_lunchcare(client, app, db):
    username, password = _get_or_create_lunchcare_user(app, db)
    _login(client, username, password)


def _create_school(app, db):
    with app.app_context():
        SchoolORMFactory._meta.sqlalchemy_session = db.session
        school = SchoolORMFactory()
        db.session.commit()
        return school.id


def _create_student(app, db, school_id):
    with app.app_context():
        StudentORMFactory._meta.sqlalchemy_session = db.session
        student = StudentORMFactory(school_id=school_id, status=1)
        db.session.commit()
        return student.id


def _create_user(app, db, username, ws_token):
    with app.app_context():
        UserORMFactory._meta.sqlalchemy_session = db.session
        user = UserORMFactory(username=username, ws_token=ws_token)
        db.session.commit()
        return user.id


def _create_holyday(app, db):
    with app.app_context():
        HolydayORMFactory._meta.sqlalchemy_session = db.session
        holyday = HolydayORMFactory()
        db.session.commit()
        return holyday.id


# ---------------------------------------------------------------------------
# School routes — /management/schools/
# ---------------------------------------------------------------------------


class TestSchoolRoutes:
    def test_list_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/schools/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_list_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/schools/")
        assert response.status_code == 200

    def test_create_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/schools/",
            data={
                "centerName": "Test School",
                "centerAddress": "Rúa 1",
                "centerPhone": "",
                "centerMail": "",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_create_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/schools/",
            data={
                "centerName": "Colexio Novo HTTP",
                "centerAddress": "Rúa Principal 1",
                "centerPhone": "666000111",
                "centerMail": "test@school.com",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_edit_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        school_id = _create_school(app, db)
        response = client.post(
            f"/management/schools/{school_id}",
            data={
                "centerName": "Updated",
                "centerAddress": "Rúa 2",
                "centerPhone": "",
                "centerMail": "",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_edit_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        response = client.post(
            f"/management/schools/{school_id}",
            data={
                "centerName": "Updated Name",
                "centerAddress": "Rúa Actualizada 2",
                "centerPhone": "666000222",
                "centerMail": "updated@school.com",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302


# ---------------------------------------------------------------------------
# Student routes — /management/students/
# ---------------------------------------------------------------------------


class TestStudentRoutes:
    def test_list_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/students/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_list_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/students/")
        assert response.status_code == 200

    def test_list_renders_school_courses(self, client, app, db):
        """Verifica que el select de cursos no está vacío — regresión del bug school_courses=[]."""
        _login_admin(client, app, db)
        with app.app_context():
            from app.infrastructure.school_course.orm import SchoolCourseORM as SchoolCourses

            has_courses = db.session.query(SchoolCourses).count() > 0
        if not has_courses:
            pytest.skip("No hay SchoolCourses en la DB de test — seed necesario")
        response = client.get("/management/students/")
        assert response.status_code == 200
        # Si school_courses=[] el HTML no tendrá <option> con id de curso
        assert b"studentClassroom" in response.data

    def test_create_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/students/",
            data={
                "studentName": "Ana",
                "studentSurname": "García",
                "selectedSchool": "1",
                "selectedIntolerancesIds": "",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_create_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        response = client.post(
            "/management/students/",
            data={
                "studentName": "Ana",
                "studentSurname": "López",
                "selectedSchool": str(school_id),
                "studentClassroom": "1A",
                "studentNumberId": "12345678A",
                "studentPhone": "",
                "studentMail": "",
                "studentAddress": "",
                "studentAllergies": "",
                "studentChildish": "no",
                "brotherNumber": "0",
                "studentNumber": "",
                "selectedIntolerancesIds": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_edit_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)
        response = client.post(
            f"/management/students/{student_id}",
            data={
                "studentName": "Updated",
                "studentSurname": "Name",
                "selectedSchool": str(school_id),
                "selectedIntolerancesIds": "",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_edit_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)
        response = client.post(
            f"/management/students/{student_id}",
            data={
                "studentName": "Updated",
                "studentSurname": "Name",
                "selectedSchool": str(school_id),
                "studentClassroom": "2B",
                "studentNumberId": "87654321B",
                "studentPhone": "",
                "studentMail": "",
                "studentAddress": "",
                "studentAllergies": "",
                "studentChildish": "no",
                "brotherNumber": "0",
                "selectedIntolerancesIds": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_get_all_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post("/management/students/all", json={"user": None})
        assert response.status_code == 302

    def test_get_all_with_admin_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post("/management/students/all", json={"user": None})
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# User routes — /management/users/
# ---------------------------------------------------------------------------


class TestUserRoutes:
    def test_list_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/users/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_list_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/users/")
        assert response.status_code == 200

    def test_create_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/users/",
            data={
                "userLogin": "newuser",
                "userPass": "password123",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_create_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/users/",
            data={
                "userLogin": "newroutes_user_001",
                "userName": "New",
                "userSurname": "User",
                "userMail": "",
                "userPhone": "",
                "numberID": "",
                "userAddress": "",
                "userPass": "password123",
                "userPartner": "",
                "selectedRolesIds": "",
                "selectedSchoolsIds": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_edit_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        user_id = _create_user(app, db, "edit_target_noauth", "edit-noauth-token")
        response = client.post(
            f"/management/users/{user_id}",
            data={
                "userName": "Updated",
                "userSurname": "User",
                "selectedRolesIds": "",
                "selectedSchoolsIds": "",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_edit_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        user_id = _create_user(app, db, "edit_target_admin", "edit-admin-token")
        response = client.post(
            f"/management/users/{user_id}",
            data={
                "userLogin": "edit_target_admin",
                "userName": "Updated",
                "userSurname": "User",
                "userMail": "",
                "userPhone": "",
                "numberID": "",
                "userAddress": "",
                "userPartner": "",
                "userPass": "",
                "selectedRolesIds": "",
                "selectedSchoolsIds": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_generate_password_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post("/management/users/generate-password")
        assert response.status_code == 302

    def test_generate_password_with_admin_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post("/management/users/generate-password")
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "password" in data

    def test_check_username_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post("/management/users/check-username", json={"username": "routes_admin"})
        assert response.status_code == 302

    def test_check_username_with_auth_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post("/management/users/check-username", json={"username": "routes_admin"})
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "success" in data
        assert data["success"] is True
        assert "exists" in data
        assert data["exists"] == 1

    def test_check_username_nonexistent_returns_exists_0(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/users/check-username", json={"username": "this_user_does_not_exist_xyz_99999"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["exists"] == 0

    def test_change_password_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/users/change-password", json={"userId": 1, "passwordOld": "a", "passwordNew": "b"}
        )
        assert response.status_code == 302

    def test_change_password_wrong_old_password_returns_false(self, client, app, db):
        _login_admin(client, app, db)
        # Get the admin user id
        from app.infrastructure.user.orm import UserORM as User

        with app.app_context():
            user = db.session.query(User).filter_by(username="routes_admin").first()
            user_id = user.id
        response = client.post(
            "/management/users/change-password",
            json={
                "userId": user_id,
                "passwordOld": "wrong_old_password",
                "passwordNew": "new_password",
                "passwordNew1": "new_password",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert data["success"] is False


# ---------------------------------------------------------------------------
# Holyday routes — /management/holydays/
# ---------------------------------------------------------------------------


class TestHolydayRoutes:
    def test_list_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/holydays/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_list_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/holydays/")
        assert response.status_code == 200

    def test_create_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/holydays/",
            data={
                "dataHolydayDateValue": "15/06/2026",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_create_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/holydays/",
            data={
                "dataHolydayDateValue": "20/06/2026",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_edit_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        holyday_id = _create_holyday(app, db)
        response = client.post(
            f"/management/holydays/{holyday_id}",
            data={
                "dataHolydayDateValue": "21/06/2026",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_edit_with_admin_redirects(self, client, app, db):
        _login_admin(client, app, db)
        holyday_id = _create_holyday(app, db)
        response = client.post(
            f"/management/holydays/{holyday_id}",
            data={
                "dataHolydayDateValue": "22/06/2026",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302


# ---------------------------------------------------------------------------
# Menu routes — /management/menu/
# ---------------------------------------------------------------------------


class TestMenuRoutes:
    def test_list_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/menu/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_list_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/menu/")
        assert response.status_code == 200

    def test_set_menu_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/menu/",
            data={
                "menu_link": "https://example.com/menu.pdf",
            },
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_set_menu_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/menu/",
            data={
                "menu_link": "https://example.com/menu.pdf",
            },
        )
        # set_menu renders template directly (200), not redirect
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Edit registers routes — /management/edit/
# ---------------------------------------------------------------------------


class TestEditRegistersRoutes:
    def test_list_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/edit/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_list_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/edit/")
        assert response.status_code == 200

    def test_find_registers_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/edit/find_registers_post",
            json={
                "register_type": 0,
                "register_student": 0,
                "register_user": 0,
                "register_from": "01/01/2026",
                "register_until": "31/01/2026",
            },
        )
        assert response.status_code == 302

    def test_find_registers_with_admin_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/edit/find_registers_post",
            json={
                "register_type": 0,
                "register_student": 0,
                "register_user": 0,
                "register_from": "01/01/2026",
                "register_until": "31/01/2026",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert isinstance(data, list)

    def test_get_register_data_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/edit/get_register_data_post",
            json={
                "register_type": "lunch",
                "register_id": 999999,
            },
        )
        assert response.status_code == 302

    def test_get_register_data_with_admin_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/management/edit/get_register_data_post",
            json={
                "register_type": "lunch",
                "register_id": 999999,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None

    def test_save_registers_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/management/edit/save_registers_post",
            json={
                "student_value": "1",
                "type_value": "3",
                "id": "0",
                "date_value": "15/01/2026",
                "register_notes": "",
                "extra": None,
                "not_come": None,
            },
        )
        assert response.status_code == 302

    def test_save_registers_with_admin_creates_record(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)
        response = client.post(
            "/management/edit/save_registers_post",
            json={
                "student_value": str(student_id),
                "type_value": "3",
                "id": "0",
                "date_value": "15/01/2026",
                "register_notes": "",
                "extra": None,
                "not_come": None,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert data["success"] is True


# ---------------------------------------------------------------------------
# Reports routes
# ---------------------------------------------------------------------------


class TestReportsRoutes:
    def test_management_reports_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/reports/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_management_reports_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/reports/")
        assert response.status_code == 200

    def test_earlycare_reports_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/earlycare-reports/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_earlycare_reports_with_earlycare_user_returns_200(self, client, app, db):
        _login_earlycare(client, app, db)
        response = client.get("/management/earlycare-reports/")
        assert response.status_code == 200

    def test_earlycare_reports_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/earlycare-reports/")
        assert response.status_code == 200

    def test_lunchcare_reports_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/management/lunchcare-reports/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_lunchcare_reports_with_lunchcare_user_returns_200(self, client, app, db):
        _login_lunchcare(client, app, db)
        response = client.get("/management/lunchcare-reports/")
        assert response.status_code == 200

    def test_lunchcare_reports_with_admin_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/lunchcare-reports/")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Auth routes — /login, /logout
# ---------------------------------------------------------------------------


class TestAuthRoutes:
    def test_get_login_page_is_public(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/login")
        assert response.status_code == 200

    def test_post_login_valid_credentials_redirects_to_root(self, client, app, db):
        _clear_login_state(app)
        _get_or_create_admin(app, db)
        response = client.post(
            "/login",
            data={
                "username": "routes_admin",
                "password": "routes_pass",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/" in response.headers["Location"]

    def test_post_login_invalid_credentials_redirects_to_login(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/login",
            data={
                "username": "routes_admin",
                "password": "wrong_password_xyz",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.headers["Location"]

    def test_logout_with_session_redirects(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 302

    def test_logout_without_session_redirects_to_login(self, client, app, db):
        _clear_login_state(app)
        # Un client nuevo sin sesión debe redirigir a /login
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 302


# ---------------------------------------------------------------------------
# Main routes — /
# ---------------------------------------------------------------------------


class TestMainRoutes:
    def test_index_without_auth_returns_200(self, client, app, db):
        _clear_login_state(app)
        # La página principal muestra el formulario de login si no está autenticado
        response = client.get("/")
        assert response.status_code == 200

    def test_index_with_auth_returns_200(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Calendar routes — /calendar/...
# ---------------------------------------------------------------------------


class TestCalendarBpRoutes:
    def test_get_calendar_events_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/calendar/events?school_id=1&date=2026-01-15")
        assert response.status_code == 302

    def test_get_calendar_events_with_auth_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/calendar/events?school_id=1&date=2026-01-15")
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert isinstance(data, list)

    def test_get_earlycare_stats_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/calendar/earlycare-stats?school_id=1&date=2026-01-15")
        assert response.status_code == 302

    def test_get_earlycare_stats_with_auth_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/calendar/earlycare-stats?school_id=1&date=2026-01-15")
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "total_requested" in data

    def test_get_lunchcare_stats_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.get("/calendar/lunchcare-stats?school_id=1&date=2026-01-15")
        assert response.status_code == 302

    def test_get_lunchcare_stats_with_auth_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/calendar/lunchcare-stats?school_id=1&date=2026-01-15")
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "total_requested" in data

    def test_save_attendance_range_no_auth_redirects(self, client, app, db):
        _clear_login_state(app)
        response = client.post(
            "/calendar/attendance-range",
            json={
                "school_id": 1,
                "date_from": "2026-01-13",
                "date_to": "2026-01-13",
                "attendances": [],
            },
        )
        assert response.status_code == 302

    def test_save_attendance_range_with_auth_returns_json(self, client, app, db):
        _login_admin(client, app, db)
        response = client.post(
            "/calendar/attendance-range",
            json={
                "school_id": 1,
                "date_from": "2026-01-13",
                "date_to": "2026-01-13",
                "attendances": [],
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "saved_dates" in data
        assert "skipped_dates" in data


# ---------------------------------------------------------------------------
# Persistencia — verifica que los datos realmente se guardan/actualizan en DB
# Estos tests previenen la regresión donde el form hace POST al endpoint
# equivocado (ej. create en vez de edit) y la respuesta es 302 igual.
# ---------------------------------------------------------------------------


def _login_admin(client, app, db):
    _get_or_create_admin(app, db)
    client.post("/login", data={"username": "routes_admin", "password": "routes_pass"})


class TestEditPersistence:
    """Verifica que POST /<id> realmente actualiza los datos en la DB."""

    def test_edit_school_persists_changes(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)

        client.post(
            f"/management/schools/{school_id}",
            data={
                "centerName": "Nombre Actualizado",
                "centerAddress": "Rúa Nova 99",
                "centerPhone": "999888777",
                "centerMail": "nuevo@school.com",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            school = db.session.get(School, school_id)
            assert school.name == "Nombre Actualizado", (
                "El nombre no se actualizó — el form envió al endpoint de crear en vez de editar"
            )
            assert school.address == "Rúa Nova 99"
            assert school.phone == "999888777"

    def test_edit_student_persists_changes(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)

        client.post(
            f"/management/students/{student_id}",
            data={
                "studentName": "NombreActualizado",
                "studentSurname": "ApellidoActualizado",
                "selectedSchool": str(school_id),
                "studentClassroom": "3",
                "selectedIntolerancesIds": "",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            student = db.session.get(Student, student_id)
            assert student.name == "NombreActualizado", (
                "El nombre no se actualizó — el form envió al endpoint de crear en vez de editar"
            )
            assert student.surname == "ApellidoActualizado"

    def test_edit_holyday_persists_changes(self, client, app, db):
        _login_admin(client, app, db)
        holyday_id = _create_holyday(app, db)

        client.post(
            f"/management/holydays/{holyday_id}",
            data={
                "dataHolydayDateValue": "02/06/2026",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.holyday.orm import HolydayORM as Holydays

            holyday = db.session.get(Holydays, holyday_id)
            # La fecha debe haberse actualizado (no seguir siendo la original)
            assert holyday.holyday.strftime("%d/%m/%Y") == "02/06/2026", (
                "La fecha no se actualizó — el form envió al endpoint de crear en vez de editar"
            )

    def test_create_school_is_separate_from_edit(self, client, app, db):
        """POST / (sin id) crea un registro nuevo — no edita el existente."""
        _login_admin(client, app, db)
        _create_school(app, db)

        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            count_before = db.session.query(School).count()

        client.post(
            "/management/schools/",
            data={
                "centerName": "Centro Nuevo",
                "centerAddress": "Rúa Nueva 1",
                "centerPhone": "111222333",
                "centerMail": "nuevo@nuevo.com",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            count_after = db.session.query(School).count()
            assert count_after == count_before + 1, "POST / debe crear un nuevo registro, no editar el existente"

    def test_edit_user_persists_changes(self, client, app, db):
        """POST /<user_id> realmente actualiza los datos del usuario en DB."""
        _login_admin(client, app, db)
        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            user = UserORMFactory(
                username="user_to_edit_persist",
                ws_token="edit-persist-token",
                name="NombreOriginal",
                surname="ApellidoOriginal",
            )
            db.session.commit()
            user_id = user.id

        client.post(
            f"/management/users/{user_id}",
            data={
                "userLogin": "user_to_edit_persist",
                "userName": "NombreActualizado",
                "userSurname": "ApellidoActualizado",
                "userMail": "",
                "userPhone": "",
                "numberID": "",
                "userAddress": "",
                "userPartner": "",
                "selectedRolesIds": "",
                "selectedSchoolsIds": "",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.user.orm import UserORM as User

            user = db.session.get(User, user_id)
            assert user.name == "NombreActualizado", (
                "El nombre no se actualizó — el form envió al endpoint de crear en vez de editar"
            )
            assert user.surname == "ApellidoActualizado"

    def test_create_user_does_not_overwrite_existing(self, client, app, db):
        """POST / (sin id) crea usuario nuevo, no sobreescribe el existente."""
        _login_admin(client, app, db)
        with app.app_context():
            from app.infrastructure.user.orm import UserORM as User

            count_before = db.session.query(User).count()

        client.post(
            "/management/users/",
            data={
                "userName": "Usuario Nuevo",
                "userSurname": "Apellido Nuevo",
                "userLogin": f"new_user_persist_{count_before}",
                "userPass": "password123",
                "userMail": "",
                "userPhone": "",
                "numberID": "",
                "userAddress": "",
                "userPartner": "",
                "selectedRolesIds": "",
                "selectedSchoolsIds": "",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.user.orm import UserORM as User

            count_after = db.session.query(User).count()
            assert count_after == count_before + 1, "POST / debe crear un nuevo usuario, no editar el existente"

    def test_edit_student_does_not_create_new(self, client, app, db):
        """POST /<student_id> edita — no crea un registro nuevo."""
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)

        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            count_before = db.session.query(Student).count()

        client.post(
            f"/management/students/{student_id}",
            data={
                "studentName": "NombreCambiado",
                "studentSurname": "ApellidoCambiado",
                "selectedSchool": str(school_id),
                "studentClassroom": "3",
                "selectedIntolerancesIds": "",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            count_after = db.session.query(Student).count()
            assert count_after == count_before, "POST /<id> no debe crear un nuevo registro — debe editar el existente"

    def test_edit_holyday_does_not_create_new(self, client, app, db):
        """POST /<holyday_id> edita — no crea un festivo nuevo."""
        _login_admin(client, app, db)
        holyday_id = _create_holyday(app, db)

        with app.app_context():
            from app.infrastructure.holyday.orm import HolydayORM as Holydays

            count_before = db.session.query(Holydays).count()

        client.post(
            f"/management/holydays/{holyday_id}",
            data={
                "dataHolydayDateValue": "15/08/2026",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.holyday.orm import HolydayORM as Holydays

            count_after = db.session.query(Holydays).count()
            assert count_after == count_before, "POST /<id> no debe crear un nuevo festivo — debe editar el existente"

    def test_set_menu_persists_link(self, client, app, db):
        """POST /management/menu/ guarda el nuevo link de menú."""
        _login_admin(client, app, db)

        client.post(
            "/management/menu/",
            data={
                "menu_link": "https://example.com/menu-actualizado",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.menu.orm import MenuORM as Menu

            menu = db.session.query(Menu).filter_by(status=1).first()
            assert menu is not None, "Debe existir un menú activo tras el POST"
            assert menu.menu_link == "https://example.com/menu-actualizado", (
                "El link del menú no se guardó correctamente"
            )


# ---------------------------------------------------------------------------
# Create persistencia — verifica que POST / realmente inserta en DB
# ---------------------------------------------------------------------------


class TestCreatePersistence:
    """Verifica que POST / realmente inserta un nuevo registro en la DB."""

    def test_create_school_inserts_record(self, client, app, db):
        _login_admin(client, app, db)
        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            count_before = db.session.query(School).count()

        client.post(
            "/management/schools/",
            data={
                "centerName": "Novo Centro Persist",
                "centerAddress": "Rúa Test 1",
                "centerPhone": "600100200",
                "centerMail": "create@test.com",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            count_after = db.session.query(School).count()
            assert count_after == count_before + 1, "POST / debe insertar un nuevo centro"
            school = db.session.query(School).filter_by(name="Novo Centro Persist").first()
            assert school is not None
            assert school.address == "Rúa Test 1"

    def test_create_student_inserts_record(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            count_before = db.session.query(Student).count()

        client.post(
            "/management/students/",
            data={
                "studentName": "Novo",
                "studentSurname": "Alumno",
                "selectedSchool": str(school_id),
                "studentClassroom": "2",
                "selectedIntolerancesIds": "",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            count_after = db.session.query(Student).count()
            assert count_after == count_before + 1, "POST / debe insertar un nuevo alumno"
            student = db.session.query(Student).filter_by(name="Novo", surname="Alumno").first()
            assert student is not None

    def test_create_holyday_inserts_record(self, client, app, db):
        _login_admin(client, app, db)
        target_date = "26/12/2099"  # fecha única, no usada en otros tests

        client.post(
            "/management/holydays/",
            data={
                "dataHolydayDateValue": target_date,
            },
            follow_redirects=False,
        )

        with app.app_context():
            from datetime import date

            from app.infrastructure.holyday.orm import HolydayORM as Holydays

            holyday = db.session.query(Holydays).filter_by(holyday=date(2099, 12, 26)).first()
            assert holyday is not None, f"El festivo del {target_date} no se insertó en la DB"

    def test_create_user_inserts_record(self, client, app, db):
        _login_admin(client, app, db)
        with app.app_context():
            from app.infrastructure.user.orm import UserORM as User

            count_before = db.session.query(User).count()

        client.post(
            "/management/users/",
            data={
                "userName": "Usuario",
                "userSurname": "Creado",
                "userLogin": "user_create_persist_unique",
                "userPass": "pass123",
                "userMail": "",
                "userPhone": "",
                "numberID": "",
                "userAddress": "",
                "userPartner": "",
                "selectedRolesIds": "",
                "selectedSchoolsIds": "",
            },
            follow_redirects=False,
        )

        with app.app_context():
            from app.infrastructure.user.orm import UserORM as User

            count_after = db.session.query(User).count()
            assert count_after == count_before + 1, "POST / debe insertar un nuevo usuario"
            user = db.session.query(User).filter_by(username="user_create_persist_unique").first()
            assert user is not None
            assert user.name == "Usuario"


# ---------------------------------------------------------------------------
# Delete persistencia — verifica que POST /<id>/delete realmente soft-elimina
# ---------------------------------------------------------------------------


class TestDeletePersistence:
    """Verifica que POST /<id>/delete realmente hace soft-delete (status=0) en DB."""

    def test_delete_school_soft_deletes(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)

        client.post(f"/management/schools/{school_id}/delete", follow_redirects=False)

        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            school = db.session.get(School, school_id)
            assert school is not None, "El registro no debe borrarse físicamente"
            assert school.status == 0, "El soft-delete debe poner status=0, no eliminar el registro"

    def test_delete_student_soft_deletes(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)

        client.post(f"/management/students/{student_id}/delete", follow_redirects=False)

        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            student = db.session.get(Student, student_id)
            assert student is not None, "El registro no debe borrarse físicamente"
            assert student.status == 0, "El soft-delete debe poner status=0"

    def test_delete_holyday_soft_deletes(self, client, app, db):
        _login_admin(client, app, db)
        holyday_id = _create_holyday(app, db)

        client.post(f"/management/holydays/{holyday_id}/delete", follow_redirects=False)

        with app.app_context():
            from app.infrastructure.holyday.orm import HolydayORM as Holydays

            holyday = db.session.get(Holydays, holyday_id)
            assert holyday is not None, "El registro no debe borrarse físicamente"
            assert holyday.status == 0, "El soft-delete debe poner status=0"

    def test_delete_user_soft_deletes(self, client, app, db):
        _login_admin(client, app, db)
        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            user = UserORMFactory(
                username="user_to_soft_delete",
                ws_token="soft-delete-token",
                status=1,
            )
            db.session.commit()
            user_id = user.id

        client.post(f"/management/users/{user_id}/delete", follow_redirects=False)

        with app.app_context():
            from app.infrastructure.user.orm import UserORM as User

            user = db.session.get(User, user_id)
            assert user is not None, "El registro no debe borrarse físicamente"
            assert user.status == 0, "El soft-delete debe poner status=0"

    def test_deleted_school_not_in_active_list(self, client, app, db):
        """Un centro borrado no debe aparecer en la lista activa."""
        _login_admin(client, app, db)
        school_id = _create_school(app, db)

        client.post(f"/management/schools/{school_id}/delete", follow_redirects=False)

        with app.app_context():
            from app.infrastructure.school.orm import SchoolORM as School

            active = db.session.query(School).filter_by(status=1, id=school_id).first()
            assert active is None, "Un centro con status=0 no debe aparecer en queries de activos"

    def test_deleted_student_not_in_active_list(self, client, app, db):
        """Un alumno borrado no debe aparecer en la lista activa."""
        _login_admin(client, app, db)
        school_id = _create_school(app, db)
        student_id = _create_student(app, db, school_id)

        client.post(f"/management/students/{student_id}/delete", follow_redirects=False)

        with app.app_context():
            from app.infrastructure.student.orm import StudentORM as Student

            active = db.session.query(Student).filter_by(status=1, id=student_id).first()
            assert active is None, "Un alumno con status=0 no debe aparecer en queries de activos"
