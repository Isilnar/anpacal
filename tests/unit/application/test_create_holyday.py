"""
Tests unitarios: CreateHolydayUseCase.

REQ-A01: CreateHolydayUseCase
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.holyday.create import CreateHolydayUseCase, DuplicateHolydayError
from app.application.holyday.dtos import HolydayCreateDTO
from app.domain.holyday.holyday import Holyday


def _make_repo(existing=None):
    repo = MagicMock()
    repo.find_by_date.return_value = existing
    repo.save.side_effect = lambda h: Holyday(id=1, holyday=h.holyday, status=h.status)
    return repo


class TestCreateHolydayUseCase:
    def test_create_new_holyday(self):
        """Scenario: Create new holyday."""
        repo = _make_repo(existing=None)
        dto = HolydayCreateDTO(holyday=date(2026, 6, 1))

        result = CreateHolydayUseCase(repo).execute(dto)

        repo.save.assert_called_once()
        assert result.holyday == date(2026, 6, 1)
        assert result.id == 1

    def test_duplicate_holyday_raises_error(self):
        """Scenario: Duplicate holyday date."""
        existing = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        repo = _make_repo(existing=existing)
        dto = HolydayCreateDTO(holyday=date(2026, 6, 1))

        with pytest.raises(DuplicateHolydayError):
            CreateHolydayUseCase(repo).execute(dto)

        repo.save.assert_not_called()
