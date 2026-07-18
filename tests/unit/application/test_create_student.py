"""
Tests de CreateStudentUseCase — REQ-A01.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.student.create import CreateStudentUseCase, DuplicateStudentError
from app.application.student.dtos import StudentCreateDTO
from tests.factories.student_factory import StudentFactory


def _make_repo(**kwargs):
    repo = MagicMock()
    repo.get_by_number_id_hash_and_school.return_value = kwargs.get("existing", None)
    repo.save.side_effect = lambda s: StudentFactory.build(id=1, name=s.name, surname=s.surname, school_id=s.school_id)
    repo.sync_intolerances.return_value = None
    return repo


def _make_crypto():
    crypto = MagicMock()
    crypto.hash_value.return_value = "hashed_nid"
    crypto.encrypt.side_effect = lambda v: f"enc:{v}"
    return crypto


def _make_dto(**kwargs):
    return StudentCreateDTO(
        name=kwargs.get("name", "Ana"),
        surname=kwargs.get("surname", "García"),
        school_id=kwargs.get("school_id", 1),
        number_id=kwargs.get("number_id", "12345678A"),
        intolerance_ids=kwargs.get("intolerance_ids", None),
    )


def test_create_student_happy_path():
    repo = _make_repo()
    crypto = _make_crypto()
    use_case = CreateStudentUseCase(repo, crypto)

    dto = _make_dto()
    student = use_case.execute(dto)

    assert student is not None
    repo.save.assert_called_once()


def test_create_student_raises_duplicate_error():
    existing = StudentFactory.build(id=99)
    repo = _make_repo(existing=existing)
    crypto = _make_crypto()
    use_case = CreateStudentUseCase(repo, crypto)

    with pytest.raises(DuplicateStudentError):
        use_case.execute(_make_dto())

    repo.save.assert_not_called()


def test_create_student_syncs_intolerances_when_provided():
    repo = _make_repo()
    crypto = _make_crypto()
    use_case = CreateStudentUseCase(repo, crypto)

    dto = _make_dto(intolerance_ids=[1, 2])
    use_case.execute(dto)

    repo.sync_intolerances.assert_called_once()


def test_create_student_no_sync_when_intolerances_is_none():
    repo = _make_repo()
    crypto = _make_crypto()
    use_case = CreateStudentUseCase(repo, crypto)

    dto = _make_dto(intolerance_ids=None)
    use_case.execute(dto)

    repo.sync_intolerances.assert_not_called()
