"""
Tests de GetAllWithAssociationUseCase — REQ-A06.
"""

from unittest.mock import MagicMock

from app.application.student.get_all_with_association import GetAllWithAssociationUseCase
from tests.factories.student_factory import StudentFactory


def test_student_associated_to_user():
    s1 = StudentFactory.build(id=1)
    s2 = StudentFactory.build(id=2)
    repo = MagicMock()
    repo.list_active_with_school.return_value = [s1, s2]
    repo.get_associations_for_user.return_value = [1]  # only s1 is associated
    use_case = GetAllWithAssociationUseCase(repo)

    result = use_case.execute(user_id=5)

    assert len(result) == 2
    s1_result = next(r for r in result if r.student.id == 1)
    s2_result = next(r for r in result if r.student.id == 2)
    assert s1_result.associated is True
    assert s2_result.associated is False


def test_student_not_associated_to_user():
    s1 = StudentFactory.build(id=10)
    repo = MagicMock()
    repo.list_active_with_school.return_value = [s1]
    repo.get_associations_for_user.return_value = []  # no associations
    use_case = GetAllWithAssociationUseCase(repo)

    result = use_case.execute(user_id=5)

    assert result[0].associated is False


def test_user_id_none_returns_all_not_associated():
    students = [StudentFactory.build(id=i) for i in range(1, 4)]
    repo = MagicMock()
    repo.list_active_with_school.return_value = students
    use_case = GetAllWithAssociationUseCase(repo)

    result = use_case.execute(user_id=None)

    assert all(r.associated is False for r in result)
    # get_associations_for_user should NOT be called when user_id is None
    repo.get_associations_for_user.assert_not_called()
