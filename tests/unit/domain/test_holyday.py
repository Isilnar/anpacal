"""
Tests unitarios del dataclass Holyday.

REQ-D01: HolydayEntity as Pure Dataclass
"""

from datetime import date, datetime

import pytest

from app.domain.holyday.holyday import Holyday


class TestHolydayConstruction:
    def test_construct_valid_holyday(self):
        """Scenario: Construct valid HolydayEntity."""
        h = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        assert h.id == 1
        assert h.holyday == date(2026, 6, 1)
        assert h.status == 1

    def test_no_sqlalchemy_or_flask_attributes(self):
        """Scenario: HolydayEntity has no SQLAlchemy or Flask attributes."""
        h = Holyday(holyday=date(2026, 6, 1))
        attrs = vars(h)
        assert "_sa_instance_state" not in attrs
        assert "is_authenticated" not in attrs

    def test_default_status_is_1(self):
        h = Holyday(holyday=date(2026, 6, 1))
        assert h.status == 1

    def test_default_id_is_none(self):
        h = Holyday(holyday=date(2026, 6, 1))
        assert h.id is None


class TestHolydayIsActive:
    def test_is_active_when_status_1(self):
        h = Holyday(holyday=date(2026, 6, 1), status=1)
        assert h.is_active() is True

    def test_not_active_when_status_0(self):
        h = Holyday(holyday=date(2026, 6, 1), status=0)
        assert h.is_active() is False


class TestHolydayGetDict:
    def test_get_dict_returns_expected_keys(self):
        h = Holyday(id=5, holyday=date(2026, 6, 1), status=1)
        d = h.get_dict()
        assert d["id"] == 5
        assert d["holyday"] == date(2026, 6, 1)
        assert d["status"] == 1
        assert "holyday_formated" in d

    def test_get_formatted_date(self):
        h = Holyday(holyday=date(2026, 6, 1))
        assert h.get_formatted_date() == "01/06/2026"
