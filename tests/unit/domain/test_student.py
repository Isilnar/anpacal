"""
Tests del dominio Student — sin DB, puro Python.

Cubre REQ-D01, REQ-D02, REQ-D03.
"""

import pytest

from app.domain.student.repositories import StudentRepository
from app.domain.student.student import Student, StudentWithAssociation
from tests.factories.student_factory import StudentFactory

# ---------------------------------------------------------------------------
# REQ-D01: StudentEntity como dataclass puro
# ---------------------------------------------------------------------------


def test_student_is_active_when_status_1():
    student = StudentFactory.build(status=1)
    assert student.is_active() is True


def test_student_is_not_active_when_status_0():
    student = StudentFactory.build(status=0)
    assert student.is_active() is False


def test_get_fullname_returns_name_and_surname():
    student = StudentFactory.build(name="Ana", surname="García")
    assert student.get_fullname() == "Ana García"


def test_get_fullname_reverse():
    student = StudentFactory.build(name="Ana", surname="García")
    assert student.get_fullname_reverse() == "García, Ana"


def test_student_has_no_sqlalchemy_or_flask_imports():
    student = StudentFactory.build()
    attrs = student.__dict__
    assert "_sa_instance_state" not in attrs
    assert "is_authenticated" not in attrs


# ---------------------------------------------------------------------------
# REQ-D02: StudentRepository es ABC — no se puede instanciar directamente
# ---------------------------------------------------------------------------


def test_student_repository_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        StudentRepository()


def test_student_repository_concrete_subclass_valid():
    class ConcreteStudentRepo(StudentRepository):
        def get_by_id(self, student_id):
            return None

        def get_by_number_id_hash_and_school(self, nid_hash, school_id):
            return None

        def list_active(self):
            return []

        def list_active_with_school(self):
            return []

        def get_associations_for_user(self, user_id):
            return []

        def save(self, student):
            return student

        def soft_delete(self, student_id):
            pass

        def sync_intolerances(self, student_id, intolerance_ids):
            pass

    repo = ConcreteStudentRepo()
    assert repo is not None


# ---------------------------------------------------------------------------
# REQ-D03: school_id como FK directo (int)
# ---------------------------------------------------------------------------


def test_school_id_is_integer():
    student = StudentFactory.build(school_id=1)
    assert isinstance(student.school_id, int)


def test_student_has_no_schools_list():
    student = StudentFactory.build()
    assert not hasattr(student, "schools")


# ---------------------------------------------------------------------------
# StudentWithAssociation
# ---------------------------------------------------------------------------


def test_student_with_association_associated_true():
    student = StudentFactory.build()
    swa = StudentWithAssociation(student=student, associated=True)
    assert swa.associated is True
    assert swa.student is student


def test_student_with_association_associated_false():
    student = StudentFactory.build()
    swa = StudentWithAssociation(student=student, associated=False)
    assert swa.associated is False
