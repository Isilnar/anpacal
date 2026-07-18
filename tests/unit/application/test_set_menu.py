"""
Tests unitarios: SetMenuUseCase.

REQ-A01: set_active llamado con menu_link correcto; retorna Menu.
"""

from unittest.mock import MagicMock

import pytest

from app.application.menu.set_menu import SetMenuUseCase
from app.domain.menu.menu import Menu


class TestSetMenuUseCase:
    def _make_repo(self, returned_menu=None):
        repo = MagicMock()
        if returned_menu is None:
            returned_menu = Menu(menu_link="/menu.json", id=1, status=1)
        repo.set_active.return_value = returned_menu
        return repo

    def test_execute_calls_set_active_with_menu_link(self):
        repo = self._make_repo()
        SetMenuUseCase(repo).execute("/new/menu.json")
        repo.set_active.assert_called_once_with("/new/menu.json")

    def test_execute_returns_menu_from_repo(self):
        expected = Menu(menu_link="/new/menu.json", id=2, status=1)
        repo = self._make_repo(returned_menu=expected)
        result = SetMenuUseCase(repo).execute("/new/menu.json")
        assert result is expected

    def test_execute_with_empty_link_passes_through(self):
        repo = self._make_repo()
        SetMenuUseCase(repo).execute("")
        repo.set_active.assert_called_once_with("")

    def test_set_active_called_once(self):
        repo = self._make_repo()
        SetMenuUseCase(repo).execute("/menu.json")
        assert repo.set_active.call_count == 1
