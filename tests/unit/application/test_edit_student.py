"""
Tests de EditStudentUseCase — REQ-A02.
"""

from unittest.mock import MagicMock

import pytest

from app.application.student.dtos import StudentEditDTO
from app.application.student.edit import EditStudentUseCase, StudentNotFoundError
from tests.factories.student_factory import StudentFactory


def _make_repo(student=None):
    repo = MagicMock()
    repo.get_by_id.return_value = student
    repo.save.side_effect = lambda s: s
    repo.sync_intolerances.return_value = None
    return repo


def _make_crypto():
    crypto = MagicMock()
    crypto.encrypt.side_effect = lambda v: f"enc:{v}"
    return crypto


def test_edit_student_non_pii_field():
    """Cambiar solo classroom no debe llamar a crypto.encrypt."""
    student = StudentFactory.build(id=1, classroom="1A", phone="600111222", email="a@b.com")
    repo = _make_repo(student=student)
    crypto = _make_crypto()
    use_case = EditStudentUseCase(repo, crypto)

    dto = StudentEditDTO(
        student_id=1,
        name=student.name,
        surname=student.surname,
        school_id=student.school_id,
        classroom="2B",
        phone=student.phone,  # same phone
        email=student.email,  # same email
    )
    use_case.execute(dto)

    repo.save.assert_called_once()
    # phone/email didn't change — encrypt should NOT have been called directly
    crypto.encrypt.assert_not_called()


def test_edit_student_pii_field_changed():
    """Cambiar phone sí actualiza el campo."""
    student = StudentFactory.build(id=1, phone="000000000", email="a@b.com")
    repo = _make_repo(student=student)
    crypto = _make_crypto()
    use_case = EditStudentUseCase(repo, crypto)

    dto = StudentEditDTO(
        student_id=1,
        name=student.name,
        surname=student.surname,
        school_id=student.school_id,
        phone="999999999",  # changed
        email=student.email,
    )
    use_case.execute(dto)
    # The new phone value should be set on the student passed to save
    saved_student = repo.save.call_args[0][0]
    assert saved_student.phone == "999999999"


def test_edit_student_not_found():
    repo = _make_repo(student=None)
    crypto = _make_crypto()
    use_case = EditStudentUseCase(repo, crypto)

    with pytest.raises(StudentNotFoundError):
        use_case.execute(StudentEditDTO(student_id=999, name="X", surname="Y", school_id=1))


def test_edit_student_email_changed():
    """Cambiar email actualiza el campo en el student."""
    student = StudentFactory.build(id=1, email="old@example.com", address="Old Address")
    repo = _make_repo(student=student)
    crypto = _make_crypto()
    use_case = EditStudentUseCase(repo, crypto)

    dto = StudentEditDTO(
        student_id=1,
        name=student.name,
        surname=student.surname,
        school_id=student.school_id,
        email="new@example.com",  # changed
    )
    use_case.execute(dto)
    saved_student = repo.save.call_args[0][0]
    assert saved_student.email == "new@example.com"


def test_edit_student_address_changed():
    """Cambiar address actualiza el campo en el student."""
    student = StudentFactory.build(id=1, email="test@test.com", address="Old Street")
    repo = _make_repo(student=student)
    crypto = _make_crypto()
    use_case = EditStudentUseCase(repo, crypto)

    dto = StudentEditDTO(
        student_id=1,
        name=student.name,
        surname=student.surname,
        school_id=student.school_id,
        address="New Street 123",  # changed
    )
    use_case.execute(dto)
    saved_student = repo.save.call_args[0][0]
    assert saved_student.address == "New Street 123"
