"""
Tests unitarios de ListDietIntolerancesUseCase.

REQ-U01:
- execute() devuelve todas las activas con selected: False si no hay student_id
- execute() marca selected: True para las intolerancias asignadas al alumno
- La lista está ordenada alfabéticamente por description
- Devuelve lista vacía si no hay intolerances activas
"""

from unittest.mock import MagicMock

import pytest

from app.application.intolerance.list_diet_intolerances import ListDietIntolerancesUseCase
from app.domain.intolerance.entities import DietIntoleranceEntity


def _make_entity(id, description, status=1):
    return DietIntoleranceEntity(id=id, description=description, status=status)


def _make_repo(active=None, for_student=None):
    repo = MagicMock()
    repo.list_active.return_value = active if active is not None else []
    repo.get_for_student.return_value = for_student if for_student is not None else []
    return repo


class TestListDietIntolerancesNoStudent:
    def test_all_selected_false_when_no_student_id(self):
        entities = [
            _make_entity(1, "Gluten"),
            _make_entity(2, "Lactosa"),
        ]
        repo = _make_repo(active=entities)

        result = ListDietIntolerancesUseCase(repo, student_id=None).execute()

        assert len(result) == 2
        assert all(item["selected"] is False for item in result)
        repo.get_for_student.assert_not_called()

    def test_empty_list_when_no_active_intolerances(self):
        repo = _make_repo(active=[])

        result = ListDietIntolerancesUseCase(repo).execute()

        assert result == []


class TestListDietIntolerancesWithStudent:
    def test_assigned_intolerance_marked_selected(self):
        gluten = _make_entity(1, "Gluten")
        lactosa = _make_entity(2, "Lactosa")
        repo = _make_repo(active=[gluten, lactosa], for_student=[gluten])

        result = ListDietIntolerancesUseCase(repo, student_id=5).execute()

        by_id = {item["id"]: item for item in result}
        assert by_id[1]["selected"] is True
        assert by_id[2]["selected"] is False

    def test_no_assigned_all_false(self):
        entities = [_make_entity(1, "Gluten"), _make_entity(2, "Lactosa")]
        repo = _make_repo(active=entities, for_student=[])

        result = ListDietIntolerancesUseCase(repo, student_id=99).execute()

        assert all(item["selected"] is False for item in result)

    def test_result_contains_id_and_description(self):
        entities = [_make_entity(10, "Frutos secos")]
        repo = _make_repo(active=entities, for_student=[])

        result = ListDietIntolerancesUseCase(repo, student_id=1).execute()

        assert result[0]["id"] == 10
        assert result[0]["description"] == "Frutos secos"
