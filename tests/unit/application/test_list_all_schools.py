"""
Tests para ListAllSchoolsUseCase.

REQ: lista todos los schools sin filtro de status.
"""

from unittest.mock import MagicMock

from app.application.school.list_all_schools import ListAllSchoolsUseCase
from app.domain.school.repositories import SchoolRepository


def _make_use_case(return_value=None):
    repo = MagicMock(spec=SchoolRepository)
    repo.list_all.return_value = return_value if return_value is not None else []
    return ListAllSchoolsUseCase(repo), repo


class TestListAllSchools:
    def test_calls_list_all(self):
        use_case, repo = _make_use_case()
        use_case.execute()
        repo.list_all.assert_called_once_with()

    def test_returns_repo_result(self):
        schools = [MagicMock(), MagicMock(), MagicMock()]
        use_case, repo = _make_use_case(return_value=schools)
        result = use_case.execute()
        assert result is schools

    def test_returns_empty_list_when_no_schools(self):
        use_case, repo = _make_use_case(return_value=[])
        result = use_case.execute()
        assert result == []
