"""
Tests unitarios: EditSchoolUseCase.

REQ-A02: EditSchoolUseCase — edita campos, repo.save() una vez.
"""

from unittest.mock import MagicMock

import pytest

from app.application.school.dtos import SchoolEditDTO
from app.application.school.edit import EditSchoolUseCase, SchoolNotFoundError
from app.domain.school.school import School


def _make_repo(existing=None):
    repo = MagicMock()
    repo.get_by_id.return_value = existing
    repo.save.side_effect = lambda s: s
    return repo


class TestEditSchoolUseCase:
    def test_edit_existing_school_calls_save_once(self):
        existing = School(id=1, name="Antes", address="Rúa A")
        repo = _make_repo(existing=existing)
        dto = SchoolEditDTO(school_id=1, name="Depois", address="Rúa B")
        use_case = EditSchoolUseCase(repo)

        result = use_case.execute(dto)

        repo.save.assert_called_once()
        assert result.name == "Depois"
        assert result.address == "Rúa B"

    def test_edit_updates_address(self):
        existing = School(id=5, name="X", address="Old")
        repo = _make_repo(existing=existing)
        dto = SchoolEditDTO(school_id=5, name="X", address="New")
        use_case = EditSchoolUseCase(repo)

        result = use_case.execute(dto)

        assert result.address == "New"

    def test_edit_non_existent_school_raises(self):
        """REQ-A02: SchoolNotFoundError si no existe."""
        repo = _make_repo(existing=None)
        dto = SchoolEditDTO(school_id=999, name="X", address="Y")
        use_case = EditSchoolUseCase(repo)

        with pytest.raises(SchoolNotFoundError):
            use_case.execute(dto)

    def test_edit_not_found_save_not_called(self):
        repo = _make_repo(existing=None)
        dto = SchoolEditDTO(school_id=999, name="X", address="Y")
        use_case = EditSchoolUseCase(repo)

        with pytest.raises(SchoolNotFoundError):
            use_case.execute(dto)

        repo.save.assert_not_called()
