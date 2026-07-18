"""
Tests unitarios para DeleteUserUseCase.

REQ-A04: soft-delete vía repo.delete(); UserNotFoundError si no existe.
"""

from unittest.mock import MagicMock

import pytest

from app.application.user.delete import DeleteUserUseCase
from app.application.user.edit import UserNotFoundError
from tests.factories.user_factory import UserFactory


class TestDeleteUserUseCase:
    def test_delete_user_calls_repository_delete(self):
        """Usuario existe → repo.delete() llamado con el id correcto."""
        existing = UserFactory.build()
        repo = MagicMock()
        repo.find_by_id.return_value = existing

        use_case = DeleteUserUseCase(repo)
        use_case.execute(1)

        repo.delete.assert_called_once_with(1)

    def test_delete_user_raises_when_not_found(self):
        """Usuario no existe → UserNotFoundError; repo.delete() NO llamado."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        use_case = DeleteUserUseCase(repo)
        with pytest.raises(UserNotFoundError):
            use_case.execute(999)

        repo.delete.assert_not_called()
