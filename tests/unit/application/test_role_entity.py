"""
Tests para el dominio Role (app/domain/user/role.py).

Cubre __str__, __eq__ (vs Role y vs str), __hash__.
"""

from app.domain.user.role import Role


class TestRoleStr:
    def test_str_returns_name(self):
        role = Role(id=1, name="admin")
        assert str(role) == "admin"


class TestRoleEquality:
    def test_eq_with_same_role(self):
        r1 = Role(id=1, name="admin")
        r2 = Role(id=2, name="admin")
        assert r1 == r2

    def test_eq_with_different_role(self):
        r1 = Role(id=1, name="admin")
        r2 = Role(id=2, name="family")
        assert r1 != r2

    def test_eq_with_string(self):
        role = Role(id=1, name="admin")
        assert role == "admin"

    def test_neq_with_different_string(self):
        role = Role(id=1, name="admin")
        assert role != "family"

    def test_eq_with_non_role_non_str_returns_not_implemented(self):
        role = Role(id=1, name="admin")
        result = role.__eq__(42)
        assert result is NotImplemented


class TestRoleHash:
    def test_hash_is_based_on_name(self):
        role = Role(id=1, name="admin")
        assert hash(role) == hash("admin")

    def test_roles_with_same_name_have_same_hash(self):
        r1 = Role(id=1, name="admin")
        r2 = Role(id=99, name="admin")
        assert hash(r1) == hash(r2)

    def test_role_can_be_used_in_set(self):
        r1 = Role(id=1, name="admin")
        r2 = Role(id=2, name="admin")
        s = {r1, r2}
        assert len(s) == 1
