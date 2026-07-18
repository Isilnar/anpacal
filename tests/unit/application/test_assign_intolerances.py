"""
Tests para AssignIntolerancesToStudentUseCase.

REQ: sincroniza intolerancias asignadas a un alumno.
"""

from unittest.mock import MagicMock

from app.application.intolerance.assign_intolerances import AssignIntolerancesToStudentUseCase
from app.domain.student.repositories import StudentRepository


def _make_use_case(student_id: int, intolerance_ids: list):
    repo = MagicMock(spec=StudentRepository)
    return AssignIntolerancesToStudentUseCase(repo, student_id, intolerance_ids), repo


class TestAssignIntolerancesToStudent:
    def test_execute_calls_sync_intolerances(self):
        use_case, repo = _make_use_case(student_id=42, intolerance_ids=[1, 2, 3])
        use_case.execute()
        repo.sync_intolerances.assert_called_once_with(42, [1, 2, 3])

    def test_execute_with_empty_list(self):
        use_case, repo = _make_use_case(student_id=7, intolerance_ids=[])
        use_case.execute()
        repo.sync_intolerances.assert_called_once_with(7, [])

    def test_execute_returns_none(self):
        use_case, repo = _make_use_case(student_id=1, intolerance_ids=[5])
        repo.sync_intolerances.return_value = None
        result = use_case.execute()
        assert result is None
