"""
Tests unitarios de GetIntolerancesForStudentUseCase.

REQ-U02:
- execute() devuelve lista de DietIntoleranceEntity para un alumno
- execute() devuelve lista vacía si el alumno no tiene intolerances
"""

from unittest.mock import MagicMock

import pytest

from app.application.intolerance.get_intolerances_for_student import GetIntolerancesForStudentUseCase
from app.domain.intolerance.entities import DietIntoleranceEntity


def _make_entity(id, description, status=1):
    return DietIntoleranceEntity(id=id, description=description, status=status)


def _make_repo(for_student=None):
    repo = MagicMock()
    repo.get_for_student.return_value = for_student if for_student is not None else []
    return repo


class TestGetIntolerancesForStudent:
    def test_returns_entities_for_student_with_intolerances(self):
        gluten = _make_entity(1, "Gluten")
        lactosa = _make_entity(2, "Lactosa")
        repo = _make_repo(for_student=[gluten, lactosa])

        result = GetIntolerancesForStudentUseCase(repo).execute(student_id=10)

        assert len(result) == 2
        assert all(isinstance(e, DietIntoleranceEntity) for e in result)
        repo.get_for_student.assert_called_once_with(10)

    def test_returns_empty_list_for_student_without_intolerances(self):
        repo = _make_repo(for_student=[])

        result = GetIntolerancesForStudentUseCase(repo).execute(student_id=99)

        assert result == []

    def test_delegates_to_repo(self):
        entity = _make_entity(5, "Soja")
        repo = _make_repo(for_student=[entity])

        GetIntolerancesForStudentUseCase(repo).execute(student_id=3)

        repo.get_for_student.assert_called_once_with(3)
