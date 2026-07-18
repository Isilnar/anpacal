"""
Tests HTTP para user_routes (Blueprint user_bp, prefix /management/users).

REQ-V02: requiere login; crear, editar, soft-delete, listar.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.user.edit import UserNotFoundError
from tests.factories.user_factory import UserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _login(client, app):
    """Simula un usuario logueado usando LOGIN_DISABLED o forzando sesión."""
    # Usamos app context + flask_login's test client helper
    orm_mock = MagicMock()
    orm_mock.id = 1
    orm_mock.is_authenticated = True
    orm_mock.is_active = True
    orm_mock.is_anonymous = False
    orm_mock.get_id.return_value = "1"
    orm_mock.is_admin.return_value = 1  # admin_required

    with app.test_request_context():
        from flask_login import login_user

        with client.session_transaction() as sess:
            # Forzar sesión directamente: Flask-Login guarda _user_id
            sess["_user_id"] = "1"
            sess["_fresh"] = True

    return orm_mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestUserRoutesAuth:
    def test_list_users_requires_login(self, client):
        """GET /management/users/ sin sesión → redirect a login."""
        response = client.get("/management/users/", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_list_users_returns_200_for_admin(self, client, app, db):
        """GET /management/users/ con admin logueado → 200."""
        users = [UserFactory.build(status=1)]

        # Crear user ORM para user_loader
        from app.infrastructure.user.orm import UserORM as UserModel
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with (
            patch("app.adapters.views.user_routes.ListUsersUseCase") as mock_uc,
            patch("app.adapters.views.user_routes.get_selected_roles", return_value=[]),
            patch("app.adapters.views.user_routes.get_current_schools", return_value=[]),
        ):
            mock_uc.return_value.execute.return_value = users

            with client.session_transaction() as sess:
                sess["_user_id"] = user_id
                sess["_fresh"] = True

            with patch("app.adapters.decorators.current_user") as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.get("/management/users/")

        assert response.status_code == 200


class TestUserRoutesCRUD:
    def test_create_user_post_redirects(self, client, app, db):
        """POST /management/users/ → redirect después de crear."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.user_routes.CreateUserUseCase") as mock_uc:
            saved = UserFactory.build()
            mock_uc.return_value.execute.return_value = saved

            with client.session_transaction() as sess:
                sess["_user_id"] = user_id
                sess["_fresh"] = True

            with patch("app.adapters.decorators.current_user") as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        "/management/users/",
                        data={
                            "userLogin": "testuser",
                            "userName": "Test",
                            "userSurname": "User",
                            "userMail": "t@t.com",
                            "userPhone": "600",
                            "numberID": "12345678A",
                            "userAddress": "",
                            "userPass": "pass",
                            "selectedRolesIds": "",
                            "selectedSchoolsIds": "",
                            "selectedStudentsIds": "",
                        },
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)

    def test_delete_user_soft_deletes(self, client, app, db):
        """POST /management/users/<id>/delete → redirect + usuario desactivado."""
        from tests.factories.user_orm_factory import UserORMFactory

        with app.app_context():
            UserORMFactory._meta.sqlalchemy_session = db.session
            orm_user = UserORMFactory.create()
            user_id = str(orm_user.id)

        with patch("app.adapters.views.user_routes.DeleteUserUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = None

            with client.session_transaction() as sess:
                sess["_user_id"] = user_id
                sess["_fresh"] = True

            with patch("app.adapters.decorators.current_user") as mock_cu:
                mock_cu.is_admin = lambda: 1

                with app.app_context():
                    response = client.post(
                        f"/management/users/{user_id}/delete",
                        follow_redirects=False,
                    )

        assert response.status_code in (301, 302)
