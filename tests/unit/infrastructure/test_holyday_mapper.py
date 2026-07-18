"""
Tests unitarios: HolydayMapper — funciones puras, sin DB.

REQ-R01: Alias resolves to existing model
REQ-R02: ORM ↔ Domain Mapper round-trip
"""

from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from app.domain.holyday.holyday import Holyday
from app.infrastructure.holyday.mapper import domain_to_orm_fields, orm_to_domain
from app.infrastructure.holyday.orm import HolydayORM


class TestHolydayORMAlias:
    def test_alias_resolves_to_existing_model(self):
        """Scenario: HolydayORM is defined directly in infrastructure/holyday/orm.py."""
        assert HolydayORM.__table_name__ == "holydays"


class TestHolydayMapper:
    def _make_mock_orm(self, id=1, holyday=date(2026, 6, 1), status=1, created_at=None):
        orm = MagicMock()
        orm.id = id
        orm.holyday = holyday
        orm.status = status
        orm.created_at = created_at
        return orm

    def test_orm_to_domain_maps_fields(self):
        orm = self._make_mock_orm(id=1, holyday=date(2026, 6, 1), status=1)
        domain = orm_to_domain(orm)

        assert domain.id == 1
        assert domain.holyday == date(2026, 6, 1)
        assert domain.status == 1

    def test_orm_to_domain_date_is_native_date(self):
        """Scenario: holyday field is native datetime.date (no string conversion)."""
        orm = self._make_mock_orm(holyday=date(2026, 6, 1))
        domain = orm_to_domain(orm)
        assert isinstance(domain.holyday, date)

    def test_domain_to_orm_fields_returns_dict(self):
        domain = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        fields = domain_to_orm_fields(domain)

        assert fields["holyday"] == date(2026, 6, 1)
        assert fields["status"] == 1

    def test_round_trip_fidelity(self):
        """Scenario: Round-trip fidelity."""
        original = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        fields = domain_to_orm_fields(original)

        # Simular ORM con los campos
        orm = self._make_mock_orm(
            id=original.id,
            holyday=fields["holyday"],
            status=fields["status"],
        )
        restored = orm_to_domain(orm)

        assert restored.holyday == original.holyday
        assert restored.status == original.status

    def test_status_defaults_to_1_when_none(self):
        orm = self._make_mock_orm(status=None)
        domain = orm_to_domain(orm)
        assert domain.status == 1
