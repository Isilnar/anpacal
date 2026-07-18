"""
Tests unitarios de GetIntolerancesStringUseCase.

REQ-U04:
- Devuelve "desc1, desc2" cuando hay intolerances (ordered alphabetically)
- Devuelve "" cuando no hay intolerances
- Devuelve una sola descripción sin separador si hay solo una
"""

from unittest.mock import MagicMock

import pytest

from app.application.intolerance.get_intolerances_string import GetIntolerancesStringUseCase
from app.domain.intolerance.entities import DietIntoleranceEntity


def _make_entity(id, description, status=1):
    return DietIntoleranceEntity(id=id, description=description, status=status)


def _make_repo(for_student=None):
    """Repo mock whose get_string_for_student delegates to get_for_student (as the ABC does)."""
    from app.domain.intolerance.repositories import DietIntoleranceRepository

    repo = MagicMock(spec=DietIntoleranceRepository)
    entities = for_student if for_student is not None else []
    # Replicate the ABC template method so use case works correctly
    repo.get_string_for_student.side_effect = lambda sid: ", ".join(sorted(e.description for e in entities))
    return repo


class TestGetIntolerancesStringMultiple:
    def test_returns_joined_descriptions_alphabetically(self):
        # Gluten before Lactosa
        repo = _make_repo(
            for_student=[
                _make_entity(2, "Lactosa"),
                _make_entity(1, "Gluten"),
            ]
        )
        result = GetIntolerancesStringUseCase(repo).execute(student_id=1)
        assert result == "Gluten, Lactosa"

    def test_returns_single_description_without_separator(self):
        repo = _make_repo(for_student=[_make_entity(1, "Lactosa")])
        result = GetIntolerancesStringUseCase(repo).execute(student_id=1)
        assert result == "Lactosa"


class TestGetIntolerancesStringEmpty:
    def test_returns_empty_string_when_no_intolerances(self):
        repo = _make_repo(for_student=[])
        result = GetIntolerancesStringUseCase(repo).execute(student_id=42)
        assert result == ""
