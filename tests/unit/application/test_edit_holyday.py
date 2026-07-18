"""
Tests unitarios: EditHolydayUseCase.

REQ-A02: EditHolydayUseCase
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.holyday.dtos import HolydayEditDTO
from app.application.holyday.edit import EditHolydayUseCase, HolydayNotFoundError
from app.domain.holyday.holyday import Holyday


class TestEditHolydayUseCase:
    def test_edit_existing_holyday(self):
        """Scenario: Edit existing holyday."""
        existing = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.side_effect = lambda h: Holyday(id=1, holyday=h.holyday, status=h.status)

        dto = HolydayEditDTO(holyday_id=1, holyday=date(2026, 7, 4))
        result = EditHolydayUseCase(repo).execute(dto)

        repo.save.assert_called_once()
        assert result.holyday == date(2026, 7, 4)

    def test_holyday_not_found_raises_error(self):
        """Scenario: Holyday not found."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        dto = HolydayEditDTO(holyday_id=99, holyday=date(2026, 7, 4))

        with pytest.raises(HolydayNotFoundError):
            EditHolydayUseCase(repo).execute(dto)
