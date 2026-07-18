"""
Tests del mapper Student — sin DB, usando stubs de StudentORM.

Cubre REQ-R02: round-trip fidelity, decrypt PII, exclude PII from domain_to_orm_fields.
"""

from unittest.mock import MagicMock, patch

from app.infrastructure.student.mapper import domain_to_orm_fields, orm_to_domain
from tests.factories.student_factory import StudentFactory


def _make_intolerance_stub(intolerance_id: int):
    si = MagicMock()
    si.intolerance_id = intolerance_id
    return si


def _make_orm_stub(**kwargs):
    """Stub mínimo de StudentORM con los campos que usa orm_to_domain."""
    orm = MagicMock()
    orm.id = kwargs.get("id", 1)
    orm.name = kwargs.get("name", "Ana")
    orm.surname = kwargs.get("surname", "García")
    orm.school_id = kwargs.get("school_id", 1)
    orm.classroom = kwargs.get("classroom", "1A")
    orm.number_id = kwargs.get("number_id", "")
    orm.number_id_hash = kwargs.get("number_id_hash", "")
    orm.phone = kwargs.get("phone", "")
    orm.email = kwargs.get("email", "")
    orm.address = kwargs.get("address", "")
    orm.allergies = kwargs.get("allergies", "")
    orm.status = kwargs.get("status", 1)
    orm.childish = kwargs.get("childish", "no")
    orm.brother_number = kwargs.get("brother_number", 0)
    orm.student_number = kwargs.get("student_number", "")
    orm.intolerances = kwargs.get("intolerances", [])
    return orm


# ---------------------------------------------------------------------------
# orm_to_domain
# ---------------------------------------------------------------------------


@patch("app.infrastructure.student.mapper.decrypt_field", side_effect=lambda v: v)
def test_orm_to_domain_maps_basic_fields(mock_decrypt):
    orm = _make_orm_stub(id=5, name="Ana", surname="García", school_id=2, classroom="2B", status=1)
    student = orm_to_domain(orm)

    assert student.id == 5
    assert student.name == "Ana"
    assert student.surname == "García"
    assert student.school_id == 2
    assert student.classroom == "2B"
    assert student.status == 1


@patch("app.infrastructure.student.mapper.decrypt_field", side_effect=lambda v: f"dec:{v}")
def test_orm_to_domain_decrypts_pii_fields(mock_decrypt):
    orm = _make_orm_stub(
        number_id="enc_nid",
        phone="enc_phone",
        email="enc_email",
        address="enc_addr",
    )
    student = orm_to_domain(orm)

    assert student.number_id == "dec:enc_nid"
    assert student.phone == "dec:enc_phone"
    assert student.email == "dec:enc_email"
    assert student.address == "dec:enc_addr"
    assert mock_decrypt.call_count >= 4


@patch("app.infrastructure.student.mapper.decrypt_field", side_effect=lambda v: v)
def test_orm_to_domain_maps_intolerance_ids(mock_decrypt):
    intolerances = [_make_intolerance_stub(10), _make_intolerance_stub(20)]
    orm = _make_orm_stub(intolerances=intolerances)
    student = orm_to_domain(orm)

    assert student.intolerance_ids == [10, 20]


@patch("app.infrastructure.student.mapper.decrypt_field", side_effect=lambda v: v)
def test_orm_to_domain_empty_intolerances(mock_decrypt):
    orm = _make_orm_stub(intolerances=[])
    student = orm_to_domain(orm)
    assert student.intolerance_ids == []


# ---------------------------------------------------------------------------
# domain_to_orm_fields
# ---------------------------------------------------------------------------


def test_domain_to_orm_fields_excludes_pii():
    student = StudentFactory.build(
        name="Ana",
        surname="García",
        school_id=1,
        classroom="1A",
        phone="600000000",
        email="ana@example.com",
        number_id="12345678A",
        address="Calle Mayor 1",
    )
    fields = domain_to_orm_fields(student)

    assert fields["name"] == "Ana"
    assert fields["surname"] == "García"
    assert fields["school_id"] == 1
    assert fields["classroom"] == "1A"
    # PII fields must NOT be in the result
    assert "phone" not in fields
    assert "email" not in fields
    assert "number_id" not in fields
    assert "address" not in fields
