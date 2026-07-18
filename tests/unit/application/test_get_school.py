"""
Tests unitarios: GetSchoolUseCase.

REQ-A04: GetSchoolUseCase — retorna School por id.
"""

from unittest.mock import MagicMock

import pytest

from app.application.school.edit import SchoolNotFoundError
from app.application.school.get import GetSchoolUseCase
from app.domain.school.school import School


def _make_repo(existing=None):
    repo = MagicMock()
    repo.get_by_id.return_value = existing
    return repo


class TestGetSchoolUseCase:
    def test_found_returns_entity(self):
        """REQ-A04: Found → retorna SchoolEntity."""
        existing = School(id=7, name="Colexio X", address="Rúa X")
        repo = _make_repo(existing=existing)
        use_case = GetSchoolUseCase(repo)

        result = use_case.execute(7)

        assert result.id == 7
        assert result.name == "Colexio X"

    def test_not_found_raises(self):
        """REQ-A04: Not found → SchoolNotFoundError."""
        repo = _make_repo(existing=None)
        use_case = GetSchoolUseCase(repo)

        with pytest.raises(SchoolNotFoundError):
            use_case.execute(999)
