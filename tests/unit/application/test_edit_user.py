"""
Tests unitarios para EditUserUseCase.

REQ-A03: actualiza campos, llama repo.save() una vez, UserNotFoundError si no existe.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.user.dtos import UserEditDTO
from app.application.user.edit import EditUserUseCase, UserNotFoundError
from tests.factories.user_factory import UserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_dto(**overrides):
    defaults = dict(
        user_id=1,
        username="testuser",
        name="Updated",
        surname="User",
        email="updated@example.com",
        phone="600000001",
        number_id="11111111A",
        address="Nueva Calle 1",
        user_partner="",
        new_password=None,
    )
    defaults.update(overrides)
    return UserEditDTO(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestEditUserUseCase:
    def test_edit_user_updates_fields(self):
        """Usuario existe → repo.save() llamado con los nuevos valores."""
        existing = UserFactory.build()
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.return_value = existing
        crypto = MagicMock()

        use_case = EditUserUseCase(repo, crypto)
        use_case.execute(_make_dto(user_id=1, name="Updated"))

        repo.save.assert_called_once()
        call_arg = repo.save.call_args[0][0]
        assert call_arg.name == "Updated"

    def test_edit_user_raises_when_not_found(self):
        """Usuario no existe → UserNotFoundError; repo.save() NO llamado."""
        repo = MagicMock()
        repo.find_by_id.return_value = None
        crypto = MagicMock()

        use_case = EditUserUseCase(repo, crypto)
        with pytest.raises(UserNotFoundError):
            use_case.execute(_make_dto(user_id=999))

        repo.save.assert_not_called()

    def test_edit_user_save_called_once(self):
        """repo.save() se llama exactamente una vez aunque cambien varios campos."""
        existing = UserFactory.build()
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.return_value = existing
        crypto = MagicMock()

        use_case = EditUserUseCase(repo, crypto)
        use_case.execute(_make_dto(name="A", surname="B", email="c@d.com"))

        assert repo.save.call_count == 1

    def test_edit_user_with_bcrypt_hashes_new_password(self):
        """Cuando se pasa bcrypt y new_password → usa bcrypt para hashear."""
        existing = UserFactory.build(id=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.return_value = existing
        crypto = MagicMock()

        bcrypt = MagicMock()
        bcrypt.generate_password_hash.return_value = b"hashed_pw"

        # Patch _set_password to avoid DB access
        use_case = EditUserUseCase(repo, crypto, bcrypt=bcrypt)
        with patch.object(use_case, "_set_password") as mock_set_pw:
            use_case.execute(_make_dto(user_id=1, new_password="newpass"))
            mock_set_pw.assert_called_once_with(existing.id, "hashed_pw")

        bcrypt.generate_password_hash.assert_called_once_with("newpass")

    def test_edit_user_without_bcrypt_uses_plain_password(self):
        """Cuando bcrypt es None y new_password → usa la contraseña sin hashear."""
        existing = UserFactory.build(id=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.return_value = existing
        crypto = MagicMock()

        use_case = EditUserUseCase(repo, crypto, bcrypt=None)
        with patch.object(use_case, "_set_password") as mock_set_pw:
            use_case.execute(_make_dto(user_id=1, new_password="plainpass"))
            mock_set_pw.assert_called_once_with(existing.id, "plainpass")


class TestSetPassword:
    def test_set_password_updates_orm_when_found(self):
        """_set_password: ORM found → sets password and commits."""
        existing = UserFactory.build(id=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.return_value = existing
        crypto = MagicMock()

        use_case = EditUserUseCase(repo, crypto)

        mock_orm = MagicMock()
        mock_db = MagicMock()
        mock_db.session.get.return_value = mock_orm

        with patch.dict(
            "sys.modules", {"app": MagicMock(db=mock_db), "app.infrastructure.user.orm": MagicMock(UserORM=MagicMock)}
        ):
            use_case._set_password(1, "hashed_pw")

        assert mock_orm.password == "hashed_pw"
        mock_db.session.commit.assert_called_once()

    def test_set_password_noop_when_orm_not_found(self):
        """_set_password: ORM not found → no commit, no error."""
        existing = UserFactory.build(id=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.return_value = existing
        crypto = MagicMock()

        use_case = EditUserUseCase(repo, crypto)

        mock_db = MagicMock()
        mock_db.session.get.return_value = None

        with patch.dict(
            "sys.modules", {"app": MagicMock(db=mock_db), "app.infrastructure.user.orm": MagicMock(UserORM=MagicMock)}
        ):
            use_case._set_password(999, "hashed_pw")

        mock_db.session.commit.assert_not_called()
