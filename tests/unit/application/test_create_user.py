"""
Tests unitarios para CreateUserUseCase.

REQ-A02: save() una vez, send_credentials() una vez, DuplicateUsernameError si username existe.

S01 fix: _set_password() eliminado — CreateUserUseCase ya no hace doble commit.
El password hasheado se pasa como hashed_password en el User y el repo lo persiste
en un único db.session.commit() dentro de save().
"""

from unittest.mock import MagicMock

import pytest

from app.application.user.create import CreateUserUseCase, DuplicateUsernameError
from app.application.user.dtos import UserCreateDTO
from tests.factories.user_factory import UserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_dto(**overrides):
    defaults = dict(
        username="newuser",
        name="Test",
        surname="User",
        email="test@example.com",
        phone="600123456",
        number_id="12345678A",
        address="Calle Falsa 123",
        password="secret",
        user_partner="",
    )
    defaults.update(overrides)
    return UserCreateDTO(**defaults)


def _make_repo(existing_user=None, saved_user=None):
    repo = MagicMock()
    repo.find_by_username.return_value = existing_user
    if saved_user is not None:
        repo.save.return_value = saved_user
    else:
        # save retorna un User con id asignado
        user = UserFactory.build()
        object.__setattr__(user, "id", 1)
        repo.save.return_value = user
    return repo


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCreateUserUseCase:
    def test_create_user_saves_and_returns_user(self):
        """Usuario nuevo → repo.save() llamado una vez, retorna User."""
        saved = UserFactory.build()
        object.__setattr__(saved, "id", 42)
        repo = _make_repo(existing_user=None, saved_user=saved)
        crypto = MagicMock()
        mail = MagicMock()

        use_case = CreateUserUseCase(repo, crypto, mail)
        result = use_case.execute(_make_dto())

        repo.save.assert_called_once()
        assert result is saved

    def test_create_user_calls_mail_service(self):
        """Después de crear el usuario se envían las credenciales por email."""
        saved = UserFactory.build(email="test@example.com")
        object.__setattr__(saved, "id", 42)
        repo = _make_repo(existing_user=None, saved_user=saved)
        crypto = MagicMock()
        mail = MagicMock()

        use_case = CreateUserUseCase(repo, crypto, mail)
        use_case.execute(_make_dto(email="test@example.com"))

        mail.send_credentials.assert_called_once()

    def test_create_user_raises_on_duplicate_username(self):
        """Username ya existe → DuplicateUsernameError; repo.save() NO llamado."""
        existing = UserFactory.build()
        repo = _make_repo(existing_user=existing)
        crypto = MagicMock()
        mail = MagicMock()

        use_case = CreateUserUseCase(repo, crypto, mail)
        with pytest.raises(DuplicateUsernameError):
            use_case.execute(_make_dto())

        repo.save.assert_not_called()

    def test_create_user_does_not_call_mail_when_email_empty(self):
        """Sin email → send_credentials() NO se llama."""
        saved = UserFactory.build(email="")
        object.__setattr__(saved, "id", 42)
        repo = _make_repo(existing_user=None, saved_user=saved)
        crypto = MagicMock()
        mail = MagicMock()

        use_case = CreateUserUseCase(repo, crypto, mail)
        use_case.execute(_make_dto(email=""))

        mail.send_credentials.assert_not_called()
