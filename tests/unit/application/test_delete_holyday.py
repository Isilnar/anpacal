"""
Tests unitarios: DeleteHolydayUseCase.

REQ-A03: DeleteHolydayUseCase (soft-delete)
"""

from datetime import date
from unittest.mock import MagicMock, call

import pytest

from app.application.holyday.delete import DeleteHolydayUseCase, HolydayNotFoundError
from app.domain.holyday.holyday import Holyday


class TestDeleteHolydayUseCase:
    def test_soft_delete_existing_holyday(self):
        """Scenario: Soft-delete existing holyday."""
        existing = Holyday(id=1, holyday=date(2026, 6, 1), status=1)
        repo = MagicMock()
        repo.find_by_id.return_value = existing
        repo.save.side_effect = lambda h: h

        DeleteHolydayUseCase(repo).execute(1)

        repo.save.assert_called_once()
        saved_holyday = repo.save.call_args[0][0]
        assert saved_holyday.status == 0

    def test_delete_non_existent_holyday_raises_error(self):
        """Scenario: Delete non-existent holyday."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        with pytest.raises(HolydayNotFoundError):
            DeleteHolydayUseCase(repo).execute(99)
