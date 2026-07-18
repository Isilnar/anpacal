"""
Tests unitarios para GetUserUseCase.

REQ-A05: retorna User por id; UserNotFoundError si no existe.
"""

from unittest.mock import MagicMock

import pytest

from app.application.user.edit import UserNotFoundError
from app.application.user.get import GetUserUseCase
from tests.factories.user_factory import UserFactory


class TestGetUserUseCase:
    def test_get_user_returns_user_by_id(self):
        """Usuario existe → retorna User dominio."""
        expected = UserFactory.build()
        repo = MagicMock()
        repo.find_by_id.return_value = expected

        result = GetUserUseCase(repo).execute(1)

        assert result is expected
        repo.find_by_id.assert_called_once_with(1)

    def test_get_user_raises_when_not_found(self):
        """Usuario no existe → UserNotFoundError."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            GetUserUseCase(repo).execute(999)
