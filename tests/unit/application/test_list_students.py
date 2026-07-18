"""
Tests de ListStudentsUseCase — REQ-A05.
"""

from unittest.mock import MagicMock

from app.application.student.list_students import ListStudentsUseCase
from tests.factories.student_factory import StudentFactory


def test_list_students_returns_only_active():
    active_students = [StudentFactory.build(status=1), StudentFactory.build(status=1)]
    repo = MagicMock()
    repo.list_active.return_value = active_students
    use_case = ListStudentsUseCase(repo)

    result = use_case.execute()

    assert len(result) == 2
    repo.list_active.assert_called_once()


def test_list_students_empty_when_no_active():
    repo = MagicMock()
    repo.list_active.return_value = []
    use_case = ListStudentsUseCase(repo)

    result = use_case.execute()

    assert result == []
