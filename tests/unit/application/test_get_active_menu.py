"""
Tests unitarios: GetActiveMenuUseCase.

REQ-A02: retorna Menu cuando existe; retorna None cuando no hay activo.
"""

from unittest.mock import MagicMock

import pytest

from app.application.menu.get_active_menu import GetActiveMenuUseCase
from app.domain.menu.menu import Menu


class TestGetActiveMenuUseCase:
    def test_returns_active_menu_when_exists(self):
        menu = Menu(menu_link="/menu.json", id=1, status=1)
        repo = MagicMock()
        repo.get_active.return_value = menu

        result = GetActiveMenuUseCase(repo).execute()

        assert result is menu
        repo.get_active.assert_called_once()

    def test_returns_none_when_no_active_menu(self):
        repo = MagicMock()
        repo.get_active.return_value = None

        result = GetActiveMenuUseCase(repo).execute()

        assert result is None
        repo.get_active.assert_called_once()

    def test_get_active_called_exactly_once(self):
        repo = MagicMock()
        repo.get_active.return_value = None
        GetActiveMenuUseCase(repo).execute()
        assert repo.get_active.call_count == 1
