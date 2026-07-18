"""
Tests para GetSchoolsByIdsUseCase.

REQ: obtiene schools filtrados por lista de IDs.
"""

from unittest.mock import MagicMock

from app.application.school.get_schools_by_ids import GetSchoolsByIdsUseCase
from app.domain.school.repositories import SchoolRepository


def _make_use_case(return_value=None):
    repo = MagicMock(spec=SchoolRepository)
    repo.list_by_ids.return_value = return_value if return_value is not None else []
    return GetSchoolsByIdsUseCase(repo), repo


class TestGetSchoolsByIds:
    def test_calls_list_by_ids_with_given_ids(self):
        use_case, repo = _make_use_case()
        use_case.execute([1, 2, 3])
        repo.list_by_ids.assert_called_once_with([1, 2, 3])

    def test_returns_repo_result(self):
        schools = [MagicMock(), MagicMock()]
        use_case, repo = _make_use_case(return_value=schools)
        result = use_case.execute([1, 2])
        assert result is schools

    def test_empty_ids_list(self):
        use_case, repo = _make_use_case(return_value=[])
        result = use_case.execute([])
        repo.list_by_ids.assert_called_once_with([])
        assert result == []
