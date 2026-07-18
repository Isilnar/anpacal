"""
Tests del contrato ABC de UserRepository.

Verifica que:
- UserRepository no se puede instanciar directamente.
- Una subclase que no implementa todos los métodos lanza TypeError.
- Una subclase que implementa todos los métodos puede instanciarse.
"""

import pytest

from app.domain.user.repositories import UserRepository


class _IncompleteRepo(UserRepository):
    """Subclase que NO implementa ningún método abstracto."""

    pass


class _NoSaveRepo(UserRepository):
    """Subclase que implementa todo MENOS save()."""

    def find_by_id(self, user_id): ...
    def find_by_username(self, username): ...
    def find_by_email_hash(self, email_hash): ...
    def find_by_number_id_hash(self, number_id_hash): ...
    def list_active(self): ...
    def delete(self, user_id): ...
    def get_partner_flag(self, student_id): ...


class _ConcreteRepo(UserRepository):
    """Subclase que implementa todos los métodos requeridos."""

    def find_by_id(self, user_id):
        return None

    def find_by_username(self, username):
        return None

    def find_by_email_hash(self, email_hash):
        return None

    def find_by_number_id_hash(self, number_id_hash):
        return None

    def list_active(self):
        return []

    def save(self, user):
        return user

    def delete(self, user_id): ...
    def get_partner_flag(self, student_id):
        return True

    def get_student_ids_by_user(self, user_id):
        return []


def test_user_repository_is_abstract_cannot_be_instantiated():
    with pytest.raises(TypeError):
        UserRepository()


def test_concrete_repository_must_implement_find_by_id():
    with pytest.raises(TypeError):
        _IncompleteRepo()


def test_concrete_repository_must_implement_save():
    with pytest.raises(TypeError):
        _NoSaveRepo()


def test_complete_concrete_repository_can_be_instantiated():
    repo = _ConcreteRepo()
    assert isinstance(repo, UserRepository)
