"""
Tests unitarios: GetHolydayUseCase.

REQ-A04: GetHolydayUseCase
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.holyday.get import GetHolydayUseCase, HolydayNotFoundError
from app.domain.holyday.holyday import Holyday


class TestGetHolydayUseCase:
    def test_found(self):
        """Scenario: Found."""
        existing = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing

        result = GetHolydayUseCase(repo).execute(1)

        assert result.id == 1
        assert result.holyday == date(2026, 6, 1)

    def test_not_found(self):
        """Scenario: Not found."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        with pytest.raises(HolydayNotFoundError):
            GetHolydayUseCase(repo).execute(99)
