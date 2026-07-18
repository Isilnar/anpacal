import pytest

from tests.factories.user_factory import UserFactory


def test_user_is_active_when_status_1():
    user = UserFactory.build(status=1)
    assert user.is_active() is True


def test_user_is_not_active_when_status_0():
    user = UserFactory.build(status=0)
    assert user.is_active() is False


def test_get_fullname_returns_name_and_surname():
    user = UserFactory.build(name="Pedro", surname="García")
    assert user.get_fullname() == "Pedro García"


def test_get_fullname_reverse_returns_surname_comma_name():
    user = UserFactory.build(name="Pedro", surname="García")
    assert user.get_fullname_reverse() == "García, Pedro"


def test_get_avatar_text_returns_initials():
    user = UserFactory.build(name="Pedro", surname="García")
    assert user.get_avatar_text() == "PG"


def test_get_avatar_text_single_name():
    user = UserFactory.build(name="Pedro", surname="")
    assert user.get_avatar_text() == "P"


def test_has_role_returns_true_when_role_present():
    user = UserFactory.build(roles=["admin", "family"])
    assert user.has_role("admin") is True


def test_has_role_returns_false_when_role_absent():
    user = UserFactory.build(roles=["family"])
    assert user.has_role("admin") is False


def test_is_admin_returns_true_for_admin_role():
    user = UserFactory.build(roles=["admin"])
    assert user.is_admin() is True


def test_is_family_returns_false_without_family_role():
    user = UserFactory.build(roles=["admin"])
    assert user.is_family() is False


def test_user_has_no_sqlalchemy_or_flask_login_attributes():
    user = UserFactory.build()
    attrs = user.__dict__
    assert "_sa_instance_state" not in attrs
    assert "is_authenticated" not in attrs
