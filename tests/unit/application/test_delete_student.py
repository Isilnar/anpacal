"""
Tests de DeleteStudentUseCase — REQ-A03.
"""

from unittest.mock import MagicMock

import pytest

from app.application.student.delete import DeleteStudentUseCase, StudentNotFoundError
from tests.factories.student_factory import StudentFactory


def test_soft_delete_existing_student():
    student = StudentFactory.build(id=1, status=1)
    repo = MagicMock()
    repo.get_by_id.return_value = student
    use_case = DeleteStudentUseCase(repo)

    use_case.execute(1)

    repo.soft_delete.assert_called_once_with(1)


def test_delete_non_existent_student_raises():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    use_case = DeleteStudentUseCase(repo)

    with pytest.raises(StudentNotFoundError):
        use_case.execute(999)

    repo.soft_delete.assert_not_called()
