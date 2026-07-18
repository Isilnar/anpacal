"""
SetMenuUseCase — establece el menú activo.

Delega en repo.set_active() que garantiza atomicidad:
desactiva todos los activos + inserta nuevo en un solo commit.
"""

from __future__ import annotations

from app.domain.menu.menu import Menu
from app.domain.menu.repositories import MenuRepository


class SetMenuUseCase:
    def __init__(self, repo: MenuRepository) -> None:
        self._repo = repo

    def execute(self, menu_link: str) -> Menu:
        return self._repo.set_active(menu_link)
