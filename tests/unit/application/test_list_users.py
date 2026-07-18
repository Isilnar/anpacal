"""
Tests unitarios para ListUsersUseCase.

REQ-A06: retorna solo usuarios activos; lista vacía cuando no hay ninguno.
"""

from unittest.mock import MagicMock

from app.application.user.list_users import ListUsersUseCase
from tests.factories.user_factory import UserFactory


class TestListUsersUseCase:
    def test_list_users_returns_active_users(self):
        """repo.list_active() retorna 2 usuarios → use case los devuelve todos."""
        users = [UserFactory.build(status=1), UserFactory.build(status=1)]
        repo = MagicMock()
        repo.list_active.return_value = users

        result = ListUsersUseCase(repo).execute()

        assert result == users
        repo.list_active.assert_called_once()

    def test_list_users_returns_empty_list_when_no_users(self):
        """Sin usuarios activos → retorna lista vacía."""
        repo = MagicMock()
        repo.list_active.return_value = []

        result = ListUsersUseCase(repo).execute()

        assert result == []
