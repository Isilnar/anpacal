"""
Tests de GetStudentUseCase — REQ-A04.
"""

from unittest.mock import MagicMock

import pytest

from app.application.student.get import GetStudentUseCase, StudentNotFoundError
from tests.factories.student_factory import StudentFactory


def test_get_student_found():
    student = StudentFactory.build(id=1, phone="600123456")
    repo = MagicMock()
    repo.get_by_id.return_value = student
    use_case = GetStudentUseCase(repo)

    result = use_case.execute(1)

    assert result is student
    repo.get_by_id.assert_called_once_with(1)


def test_get_student_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    use_case = GetStudentUseCase(repo)

    with pytest.raises(StudentNotFoundError):
        use_case.execute(999)
