"""
Tests unitarios del mapper School — sin DB, sin crypto.

REQ-R01: SchoolORM as alias.
REQ-R02: ORM ↔ Domain Mapper (trivial, no decrypt_field).
"""

from datetime import datetime
from unittest.mock import MagicMock

from app.domain.school.school import School
from app.infrastructure.school.mapper import domain_to_orm_fields, orm_to_domain
from app.infrastructure.school.orm import SchoolORM


class TestSchoolORMAlias:
    def test_alias_resolves_to_same_class(self):
        """REQ-R01: SchoolORM is defined directly in infrastructure/school/orm.py."""
        assert SchoolORM.__tablename__ == "school"


class TestOrmToDomain:
    def _make_orm(self, **kwargs):
        orm = MagicMock()
        orm.id = kwargs.get("id", 1)
        orm.created_at = kwargs.get("created_at", datetime(2024, 1, 1))
        orm.name = kwargs.get("name", "Colexio A")
        orm.address = kwargs.get("address", "Rúa 1")
        orm.phone = kwargs.get("phone", "981000000")
        orm.email = kwargs.get("email", "info@colexio.gal")
        orm.status = kwargs.get("status", 1)
        return orm

    def test_maps_all_fields(self):
        orm = self._make_orm()
        domain = orm_to_domain(orm)
        assert domain.id == 1
        assert domain.name == "Colexio A"
        assert domain.address == "Rúa 1"
        assert domain.phone == "981000000"
        assert domain.email == "info@colexio.gal"
        assert domain.status == 1

    def test_none_name_becomes_empty_string(self):
        orm = self._make_orm(name=None)
        domain = orm_to_domain(orm)
        assert domain.name == ""

    def test_none_status_defaults_to_1(self):
        orm = self._make_orm(status=None)
        domain = orm_to_domain(orm)
        assert domain.status == 1

    def test_no_decrypt_calls(self):
        """Mapper trivial — no debe importar ni llamar decrypt_field/encrypt_field."""
        import ast
        import textwrap

        import app.infrastructure.school.mapper as mapper_module

        source = open(mapper_module.__file__).read()
        tree = ast.parse(source)
        # Recolectar todos los nombres de funciones/atributos llamados
        calls = {
            node.attr if isinstance(node, ast.Attribute) else node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute | ast.Name)
        }
        assert "decrypt_field" not in calls
        assert "encrypt_field" not in calls


class TestDomainToOrmFields:
    def test_returns_all_updatable_fields(self):
        domain = School(name="B", address="Rúa 2", phone="123", email="b@b.com", status=0)
        fields = domain_to_orm_fields(domain)
        assert fields["name"] == "B"
        assert fields["address"] == "Rúa 2"
        assert fields["phone"] == "123"
        assert fields["email"] == "b@b.com"
        assert fields["status"] == 0

    def test_round_trip_fidelity(self):
        """REQ-R02: Round-trip to_domain(to_orm_fields(entity)) preserves fields."""
        original = School(id=7, name="Round", address="Trip", phone="999", email="r@t.com", status=1)
        fields = domain_to_orm_fields(original)

        orm = MagicMock()
        orm.id = original.id
        orm.created_at = None
        for k, v in fields.items():
            setattr(orm, k, v)

        restored = orm_to_domain(orm)
        assert restored.name == original.name
        assert restored.address == original.address
        assert restored.phone == original.phone
        assert restored.email == original.email
        assert restored.status == original.status
