"""
Tests unitarios del domain Menu dataclass.

REQ-D01: MenuEntity como dataclass pura sin dependencias de framework.
"""

from datetime import datetime

import pytest

from app.domain.menu.menu import Menu


class TestMenuDataclass:
    def test_construct_valid_menu(self):
        m = Menu(menu_link="/static/menu/menu.json", id=1, status=1)
        assert m.id == 1
        assert m.menu_link == "/static/menu/menu.json"
        assert m.status == 1

    def test_is_active_returns_true_when_status_1(self):
        m = Menu(menu_link="/menu.json", status=1)
        assert m.is_active() is True

    def test_is_active_returns_false_when_status_0(self):
        m = Menu(menu_link="/menu.json", status=0)
        assert m.is_active() is False

    def test_default_status_is_1(self):
        m = Menu(menu_link="/menu.json")
        assert m.status == 1

    def test_id_defaults_to_none(self):
        m = Menu(menu_link="/menu.json")
        assert m.id is None

    def test_created_at_defaults_to_none(self):
        m = Menu(menu_link="/menu.json")
        assert m.created_at is None

    def test_get_dict_returns_expected_keys(self):
        m = Menu(menu_link="/menu.json", id=5, status=1)
        d = m.get_dict()
        assert d == {"id": 5, "menu_link": "/menu.json", "status": 1}

    def test_no_sqlalchemy_attributes(self):
        m = Menu(menu_link="/menu.json")
        assert "_sa_instance_state" not in m.__dict__

    def test_no_flask_login_attributes(self):
        m = Menu(menu_link="/menu.json")
        assert "is_authenticated" not in dir(m)
