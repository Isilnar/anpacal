"""
Tests unitarios: DeleteSchoolUseCase.

REQ-A03: DeleteSchoolUseCase — soft-delete (status=0), repo.save() una vez.
"""

from unittest.mock import MagicMock

import pytest

from app.application.school.delete import DeleteSchoolUseCase
from app.application.school.edit import SchoolNotFoundError
from app.domain.school.school import School


def _make_repo(existing=None):
    repo = MagicMock()
    repo.get_by_id.return_value = existing
    return repo


class TestDeleteSchoolUseCase:
    def test_soft_delete_existing_school(self):
        """REQ-A03: soft_delete() se llama con school_id."""
        existing = School(id=3, name="X", address="Y", status=1)
        repo = _make_repo(existing=existing)
        use_case = DeleteSchoolUseCase(repo)

        use_case.execute(3)

        repo.soft_delete.assert_called_once_with(3)

    def test_soft_delete_sets_status_0_via_repo(self):
        """repo.soft_delete() — no save() directo."""
        existing = School(id=3, name="X", address="Y", status=1)
        repo = _make_repo(existing=existing)
        use_case = DeleteSchoolUseCase(repo)

        use_case.execute(3)

        repo.save.assert_not_called()
        repo.soft_delete.assert_called_once()

    def test_delete_non_existent_raises(self):
        """REQ-A03: SchoolNotFoundError si no existe."""
        repo = _make_repo(existing=None)
        use_case = DeleteSchoolUseCase(repo)

        with pytest.raises(SchoolNotFoundError):
            use_case.execute(999)

    def test_delete_not_found_soft_delete_not_called(self):
        repo = _make_repo(existing=None)
        use_case = DeleteSchoolUseCase(repo)

        with pytest.raises(SchoolNotFoundError):
            use_case.execute(999)

        repo.soft_delete.assert_not_called()
