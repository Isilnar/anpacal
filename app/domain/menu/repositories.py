"""
MenuRepository — interfaz de dominio (ABC).

Las implementaciones concretas viven en infrastructure/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.menu.menu import Menu


class MenuRepository(ABC):
    @abstractmethod
    def get_active(self) -> Menu | None:
        """Retorna el Menu con status=1, o None si no hay ninguno."""
        ...

    @abstractmethod
    def set_active(self, menu_link: str) -> Menu:
        """
        Desactiva todos los menus activos (status=0) e inserta uno nuevo
        con el menu_link dado (status=1). Un solo commit atómico.
        """
        ...

    @abstractmethod
    def get_by_id(self, menu_id: int) -> Menu | None:
        """Retorna el Menu con el id dado, o None si no existe."""
        ...
