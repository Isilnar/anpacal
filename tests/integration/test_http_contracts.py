"""
HTTP contract tests — verifica que cada endpoint JSON devuelve exactamente
los campos que el frontend (JS en templates) espera.

Estos tests previenen la regresión donde el backend cambia un nombre de campo
(ej. intolerance_ids vs intolerances) y el template JS falla silenciosamente.
"""

import pytest

from tests.factories.holyday_orm_factory import HolydayORMFactory
from tests.factories.school_orm_factory import SchoolORMFactory
from tests.factories.student_orm_factory import StudentORMFactory
from tests.factories.user_orm_factory import UserORMFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _login_admin(client, app, db):
    """Crea un usuario admin (idempotente) y loguea en el test client."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        # Idempotente: solo crear si no existe
        user = db.session.query(User).filter_by(username="contract_admin").first()
        if not user:
            role = db.session.query(Role).filter_by(name="admin").first()
            if not role:
                role = Role(name="admin", description="Administrador")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="contract_admin",
                password=bcrypt.generate_password_hash("contract_pass").decode("utf-8"),
                name="Contract",
                surname="Admin",
                status=1,
                ws_token="contract-token-unique",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    client.post("/login", data={"username": "contract_admin", "password": "contract_pass"})


def _setup_factory(factory_cls, db, app, **kwargs):
    """Crea un objeto via factory en el contexto de la app."""
    with app.app_context():
        factory_cls._meta.sqlalchemy_session = db.session
        obj = factory_cls(**kwargs)
        db.session.commit()
        return obj.id


# ---------------------------------------------------------------------------
# school_bp.get_school — GET /management/schools/<id>
# Campos esperados por edit_school.html: name, phone, email, address
# ---------------------------------------------------------------------------


class TestGetSchoolContract:
    def test_returns_required_fields(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _setup_factory(
            SchoolORMFactory, db, app, name="Test School", phone="123", email="a@b.com", address="Rúa 1"
        )

        response = client.get(f"/management/schools/{school_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None, "El endpoint debe devolver JSON"

        # Campos que edit_school.html usa explícitamente
        for field in ("name", "phone", "email", "address"):
            assert field in data, f"Campo '{field}' falta en la respuesta de get_school"

    def test_returns_404_for_unknown_id(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/schools/999999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# student_bp.get_student — GET /management/students/<id>
# Campos esperados por edit_student.html JS:
#   name, surname, childish, brother_number, classroom, school_id,
#   number_id, phone, email, address, intolerance_ids
# ---------------------------------------------------------------------------


class TestGetStudentContract:
    def test_returns_required_fields(self, client, app, db):
        _login_admin(client, app, db)

        with app.app_context():
            SchoolORMFactory._meta.sqlalchemy_session = db.session
            school = SchoolORMFactory()
            db.session.commit()
            school_id = school.id

        student_id = _setup_factory(
            StudentORMFactory, db, app, name="Ana", surname="López", school_id=school_id, status=1
        )

        response = client.get(f"/management/students/{student_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None

        # Campos que loadStudent() en edit_student.html usa explícitamente
        for field in (
            "name",
            "surname",
            "childish",
            "brother_number",
            "classroom",
            "school_id",
            "number_id",
            "phone",
            "email",
            "address",
        ):
            assert field in data, f"Campo '{field}' falta en la respuesta de get_student"

        # intolerance_ids es lista (no 'intolerances') — el bug que ya ocurrió
        assert "intolerance_ids" in data, (
            "Campo 'intolerance_ids' falta — el template usa fillIntolerances(data.intolerance_ids)"
        )
        assert isinstance(data["intolerance_ids"], list), "'intolerance_ids' debe ser una lista"

    def test_returns_404_for_unknown_id(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/students/999999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# holyday_bp.get_holyday — GET /management/holydays/<id>
# Campos esperados por edit_holydays.html JS: date (o date_str)
# ---------------------------------------------------------------------------


class TestGetHolydayContract:
    def test_returns_required_fields(self, client, app, db):
        _login_admin(client, app, db)
        holyday_id = _setup_factory(HolydayORMFactory, db, app)

        response = client.get(f"/management/holydays/{holyday_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None

        # loadHolyday() en edit_holydays.html usa data_array["holyday_formated"]
        assert "holyday_formated" in data, "Campo 'holyday_formated' falta en la respuesta de get_holyday"

    def test_returns_404_for_unknown_id(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/holydays/999999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# user_bp.get_user — GET /management/users/<id>
# Campos esperados por edit_user.html JS:
#   name, surname, username, phone, email, address, number_id,
#   roles (lista), students (lista)
# ---------------------------------------------------------------------------


class TestGetUserContract:
    def test_returns_required_fields(self, client, app, db):
        _login_admin(client, app, db)
        user_id = _setup_factory(
            UserORMFactory, db, app, username="target_user_contract", ws_token="target-token-contract"
        )

        response = client.get(f"/management/users/{user_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None

        # Campos básicos que loadUser() usa explícitamente
        # Nota: 'password' fue eliminado intencionalmente del contrato (seguridad — no exponer hash)
        for field in (
            "name",
            "surname",
            "username",
            "phone",
            "email",
            "address",
            "number_id",
            "user_partner",
            "status",
        ):
            assert field in data, f"Campo '{field}' falta en la respuesta de get_user"

        assert "password" not in data, "get_user NO debe exponer el hash de la contraseña"

        # roles con is_selected — populateRoleModal() necesita [{id, name, is_selected}]
        assert "roles" in data, "Campo 'roles' falta"
        assert isinstance(data["roles"], list)
        if data["roles"]:
            assert "is_selected" in data["roles"][0], (
                "roles debe contener objetos con is_selected — el template usa roles[i]['is_selected']"
            )

        # schools con is_selected — populateSchoolModal() necesita [{id, name, is_selected}]
        assert "schools" in data, "Campo 'schools' falta — el template llama populateSchoolModal(data.schools)"
        assert isinstance(data["schools"], list)

        # students_associated — populateStudentModal() + campo de texto
        assert "students_associated" in data, (
            "Campo 'students_associated' falta — el template rellena el input de alumnos"
        )
        assert "students_associated_ids" in data, "Campo 'students_associated_ids' falta — el template guarda los IDs"
        assert isinstance(data["roles"], list)

    def test_returns_404_for_unknown_id(self, client, app, db):
        _login_admin(client, app, db)
        response = client.get("/management/users/999999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE endpoints — POST /<id>/delete devuelve redirect, no 404/405
# Cubre el bug donde deleteCenter() enviaba al endpoint de crear
# ---------------------------------------------------------------------------


class TestDeleteEndpointsExist:
    def test_delete_school_endpoint_exists(self, client, app, db):
        _login_admin(client, app, db)
        school_id = _setup_factory(SchoolORMFactory, db, app, name="To Delete")
        response = client.post(f"/management/schools/{school_id}/delete")
        # Debe redirigir (302) o devolver 200 — nunca 404 ni 405
        assert response.status_code in (200, 302), (
            f"DELETE school devolvió {response.status_code} — endpoint no encontrado o método incorrecto"
        )

    def test_delete_student_endpoint_exists(self, client, app, db):
        _login_admin(client, app, db)
        with app.app_context():
            SchoolORMFactory._meta.sqlalchemy_session = db.session
            school = SchoolORMFactory()
            db.session.commit()
            school_id = school.id
        student_id = _setup_factory(StudentORMFactory, db, app, school_id=school_id, status=1)
        response = client.post(f"/management/students/{student_id}/delete")
        assert response.status_code in (200, 302), f"DELETE student devolvió {response.status_code}"

    def test_delete_holyday_endpoint_exists(self, client, app, db):
        _login_admin(client, app, db)
        holyday_id = _setup_factory(HolydayORMFactory, db, app)
        response = client.post(f"/management/holydays/{holyday_id}/delete")
        assert response.status_code in (200, 302), f"DELETE holyday devolvió {response.status_code}"

    def test_delete_user_endpoint_exists(self, client, app, db):
        _login_admin(client, app, db)
        user_id = _setup_factory(
            UserORMFactory, db, app, username="user_to_delete_contract", ws_token="delete-token-contract"
        )
        response = client.post(f"/management/users/{user_id}/delete")
        assert response.status_code in (200, 302), f"DELETE user devolvió {response.status_code}"
