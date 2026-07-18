"""
Tests unitarios: ListHolydaysUseCase.

REQ-A05: ListHolydaysUseCase — returns active holydays ordered by date asc.
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.application.holyday.list_holydays import ListHolydaysUseCase
from app.domain.holyday.holyday import Holyday


class TestListHolydaysUseCase:
    def test_returns_only_active_holydays_ordered_asc(self):
        """Scenario: Returns only active holydays ordered by date asc."""
        # repo.list_active() ya filtra y ordena — eso es responsabilidad del repositorio
        active = [
            Holyday(id=1, holyday=date(2026, 5, 1), status=1),
            Holyday(id=2, holyday=date(2026, 6, 1), status=1),
        ]
        repo = MagicMock()
        repo.list_active.return_value = active

        result = ListHolydaysUseCase(repo).execute()

        repo.list_active.assert_called_once()
        assert len(result) == 2
        assert result[0].holyday == date(2026, 5, 1)
        assert result[1].holyday == date(2026, 6, 1)

    def test_returns_empty_list_when_no_active(self):
        repo = MagicMock()
        repo.list_active.return_value = []

        result = ListHolydaysUseCase(repo).execute()

        assert result == []
