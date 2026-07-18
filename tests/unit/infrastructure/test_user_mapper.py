"""
Tests del mapper User — sin DB, usando objetos stub de UserORM.

Estrategia: usar MagicMock para simular UserORM y sus relaciones
(roles como lista de asociaciones), y mockear decrypt_field para
aislar el mapper de la infraestructura criptográfica.
"""

from unittest.mock import MagicMock, patch

from app.infrastructure.user.mapper import domain_to_orm_fields, orm_to_domain
from tests.factories.user_factory import UserFactory


def _make_role_assoc(name: str):
    """Crea un stub de UserRoleAssociation con un role stub."""
    role = MagicMock()
    role.name = name
    assoc = MagicMock()
    assoc.role = role
    return assoc


def _make_orm_stub(**kwargs):
    """Stub mínimo de UserORM con los campos que usa orm_to_domain."""
    orm = MagicMock()
    orm.id = kwargs.get("id", 1)
    orm.username = kwargs.get("username", "pedro")
    orm.name = kwargs.get("name", "Pedro")
    orm.surname = kwargs.get("surname", "García")
    orm.email = kwargs.get("email", "pedro@example.com")
    orm.phone = kwargs.get("phone", "600123456")
    orm.number_id = kwargs.get("number_id", "12345678A")
    orm.address = kwargs.get("address", "Calle Mayor 1")
    orm.status = kwargs.get("status", 1)
    orm.user_partner = kwargs.get("user_partner", "")
    orm.ws_token = kwargs.get("ws_token", None)
    orm.roles = kwargs.get("roles", [])
    return orm


# ---------------------------------------------------------------------------
# orm_to_domain
# ---------------------------------------------------------------------------


@patch("app.infrastructure.user.mapper.decrypt_field", side_effect=lambda v: v)
def test_orm_to_domain_maps_id_username_name_surname(mock_decrypt):
    orm = _make_orm_stub(id=42, username="jdoe", name="John", surname="Doe")
    user = orm_to_domain(orm)

    assert user.id == 42
    assert user.username == "jdoe"
    assert user.name == "John"
    assert user.surname == "Doe"


@patch("app.infrastructure.user.mapper.decrypt_field", side_effect=lambda v: v)
def test_orm_to_domain_maps_roles_as_list_of_strings(mock_decrypt):
    roles = [_make_role_assoc("admin"), _make_role_assoc("family")]
    orm = _make_orm_stub(roles=roles)
    user = orm_to_domain(orm)

    assert user.roles == ["admin", "family"]


@patch("app.infrastructure.user.mapper.decrypt_field", side_effect=lambda v: f"decrypted:{v}")
def test_orm_to_domain_decrypts_pii_fields(mock_decrypt):
    orm = _make_orm_stub(email="enc_email", phone="enc_phone", number_id="enc_id")
    user = orm_to_domain(orm)

    # decrypt_field debe haberse llamado para cada campo PII
    assert mock_decrypt.call_count >= 3
    assert user.email == "decrypted:enc_email"
    assert user.phone == "decrypted:enc_phone"
    assert user.number_id == "decrypted:enc_id"


# ---------------------------------------------------------------------------
# domain_to_orm_fields
# ---------------------------------------------------------------------------


def test_domain_to_orm_fields_returns_non_pii_fields():
    user = UserFactory.build(
        username="jdoe",
        name="John",
        surname="Doe",
        address="Elm St",
        status=1,
        user_partner="partner_x",
    )
    fields = domain_to_orm_fields(user)

    assert fields["username"] == "jdoe"
    assert fields["name"] == "John"
    assert fields["surname"] == "Doe"
    assert fields["address"] == "Elm St"
    assert fields["status"] == 1
    assert fields["user_partner"] == "partner_x"


def test_domain_to_orm_fields_excludes_email_phone_number_id():
    user = UserFactory.build(
        email="secret@example.com",
        phone="600000000",
        number_id="99999999Z",
    )
    fields = domain_to_orm_fields(user)

    assert "email" not in fields
    assert "phone" not in fields
    assert "number_id" not in fields
    # id tampoco debe estar (el repo lo maneja a través del ORM)
    assert "id" not in fields
