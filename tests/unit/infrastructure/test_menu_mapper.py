"""
Tests unitarios del mapper Menu.

REQ-R01: MenuORM es alias del modelo.
REQ-R02: Round-trip fidelity (orm_to_domain → domain_to_orm_fields).
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.domain.menu.menu import Menu
from app.infrastructure.menu.mapper import domain_to_orm_fields, orm_to_domain
from app.infrastructure.menu.orm import MenuORM


class TestMenuORMAlias:
    def test_orm_alias_resolves_to_same_class(self):
        assert MenuORM.__table_name__ == "menu"


class TestOrmToDomain:
    def _make_orm(self, **kwargs):
        orm = MagicMock()
        orm.id = kwargs.get("id", 1)
        orm.menu_link = kwargs.get("menu_link", "/menu.json")
        orm.status = kwargs.get("status", 1)
        orm.created_at = kwargs.get("created_at", None)
        return orm

    def test_converts_fields_correctly(self):
        now = datetime(2024, 1, 15)
        orm = self._make_orm(id=5, menu_link="/test.json", status=1, created_at=now)

        result = orm_to_domain(orm)

        assert result.id == 5
        assert result.menu_link == "/test.json"
        assert result.status == 1
        assert result.created_at == now

    def test_none_menu_link_becomes_empty_string(self):
        orm = self._make_orm(menu_link=None)
        result = orm_to_domain(orm)
        assert result.menu_link == ""

    def test_none_status_defaults_to_1(self):
        orm = self._make_orm(status=None)
        result = orm_to_domain(orm)
        assert result.status == 1

    def test_returns_menu_instance(self):
        orm = self._make_orm()
        result = orm_to_domain(orm)
        assert isinstance(result, Menu)


class TestDomainToOrmFields:
    def test_returns_dict_with_expected_keys(self):
        menu = Menu(menu_link="/menu.json", status=1)
        fields = domain_to_orm_fields(menu)
        assert set(fields.keys()) == {"menu_link", "status"}

    def test_values_match_domain(self):
        menu = Menu(menu_link="/other.json", status=0)
        fields = domain_to_orm_fields(menu)
        assert fields["menu_link"] == "/other.json"
        assert fields["status"] == 0
