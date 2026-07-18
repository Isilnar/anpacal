"""
Tests unitarios para AuthenticateUserUseCase.

REQ-A01: Valid credentials → UserEntity; wrong password / unknown user → AuthenticationError.
"""

from unittest.mock import MagicMock

import pytest

from app.application.user.authenticate import AuthenticateUserUseCase, AuthenticationError
from tests.factories.user_factory import UserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_repo(orm_user=None, domain_user=None):
    """Crea un mock de repositorio con get_orm_by_username y find_by_username."""
    repo = MagicMock()
    repo.get_orm_by_username.return_value = orm_user
    repo.find_by_username.return_value = domain_user
    return repo


def _make_orm_user(check_password_result=True, status=1):
    """Crea un mock de UserORM con check_password y status."""
    orm = MagicMock()
    orm.check_password.return_value = check_password_result
    orm.status = status
    return orm


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAuthenticateUserUseCase:
    def test_authenticate_returns_user_when_credentials_valid(self):
        """Credenciales correctas → retorna User dominio."""
        domain_user = UserFactory.build()
        orm_user = _make_orm_user(check_password_result=True)
        repo = _make_repo(orm_user=orm_user, domain_user=domain_user)

        use_case = AuthenticateUserUseCase(repo)
        result = use_case.execute(domain_user.username, "correct_pass")

        assert result is domain_user
        repo.get_orm_by_username.assert_called_once_with(domain_user.username)
        orm_user.check_password.assert_called_once_with("correct_pass")

    def test_authenticate_raises_when_user_not_found(self):
        """Username desconocido → AuthenticationError."""
        repo = _make_repo(orm_user=None)

        use_case = AuthenticateUserUseCase(repo)
        with pytest.raises(AuthenticationError):
            use_case.execute("nonexistent", "any_pass")

    def test_authenticate_raises_when_password_wrong(self):
        """Password incorrecto → AuthenticationError."""
        orm_user = _make_orm_user(check_password_result=False)
        repo = _make_repo(orm_user=orm_user)

        use_case = AuthenticateUserUseCase(repo)
        with pytest.raises(AuthenticationError):
            use_case.execute("existing_user", "wrong_pass")

    def test_authenticate_raises_when_user_inactive(self):
        """Usuario inactivo (status=0) → AuthenticationError."""
        orm_user = _make_orm_user(check_password_result=True, status=0)
        repo = _make_repo(orm_user=orm_user)

        use_case = AuthenticateUserUseCase(repo)
        with pytest.raises(AuthenticationError):
            use_case.execute("inactive_user", "correct_pass")

    def test_authenticate_raises_when_domain_user_not_found_after_check(self):
        """Password ok pero find_by_username devuelve None → AuthenticationError (line 59)."""
        orm_user = _make_orm_user(check_password_result=True, status=1)
        # find_by_username returns None (anomalous state)
        repo = _make_repo(orm_user=orm_user, domain_user=None)

        use_case = AuthenticateUserUseCase(repo)
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            use_case.execute("existing_user", "correct_pass")
