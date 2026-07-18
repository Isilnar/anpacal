"""
GetActiveMenuUseCase — retorna el menu activo o None.
"""

from __future__ import annotations

from app.domain.menu.menu import Menu
from app.domain.menu.repositories import MenuRepository


class GetActiveMenuUseCase:
    def __init__(self, repo: MenuRepository) -> None:
        self._repo = repo

    def execute(self) -> Menu | None:
        return self._repo.get_active()
