"""
Tests unitarios: ListSchoolsUseCase.

REQ-A05: ListSchoolsUseCase — retorna solo schools activos (status=1).
"""

from unittest.mock import MagicMock

from app.application.school.list_schools import ListSchoolsUseCase
from app.domain.school.school import School


def _make_repo(schools):
    repo = MagicMock()
    repo.list_active.return_value = schools
    return repo


class TestListSchoolsUseCase:
    def test_returns_only_active_schools(self):
        """REQ-A05: 3 schools: 2 activos, 1 borrado → retorna 2."""
        activos = [
            School(id=1, name="A", address="Rúa A", status=1),
            School(id=2, name="B", address="Rúa B", status=1),
        ]
        repo = _make_repo(activos)
        use_case = ListSchoolsUseCase(repo)

        result = use_case.execute()

        assert len(result) == 2
        assert all(s.status == 1 for s in result)

    def test_returns_empty_when_no_active(self):
        repo = _make_repo([])
        use_case = ListSchoolsUseCase(repo)

        result = use_case.execute()

        assert result == []

    def test_calls_list_active_on_repo(self):
        repo = _make_repo([])
        use_case = ListSchoolsUseCase(repo)

        use_case.execute()

        repo.list_active.assert_called_once()
