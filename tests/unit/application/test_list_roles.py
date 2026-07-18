"""
Tests unitarios de ListRolesUseCase.

REQ-R04:
- execute() devuelve todos los roles con is_selected: False si no hay user_id
- execute() marca is_selected: True para los roles asignados al usuario
- El rol "admin" se mueve al final de la lista
- Devuelve lista vacía si no hay roles
"""

from unittest.mock import MagicMock, patch

import pytest

from app.application.role.list_roles import ListRolesUseCase
from app.domain.role.entities import RoleEntity


def _make_entity(id, name, description=""):
    return RoleEntity(id=id, name=name, description=description)


def _make_repo(roles=None):
    repo = MagicMock()
    repo.list_all.return_value = roles if roles is not None else []
    return repo


class TestListRolesNoUser:
    def test_all_is_selected_false_when_no_user_id(self):
        entities = [
            _make_entity(1, "family"),
            _make_entity(2, "lunchcare"),
        ]
        repo = _make_repo(roles=entities)

        result = ListRolesUseCase(repo, user_id=None).execute()

        assert len(result) == 2
        assert all(item["is_selected"] is False for item in result)

    def test_empty_list_when_no_roles(self):
        repo = _make_repo(roles=[])

        result = ListRolesUseCase(repo).execute()

        assert result == []

    def test_result_contains_required_keys(self):
        entities = [_make_entity(1, "admin", "Administrator")]
        repo = _make_repo(roles=entities)

        result = ListRolesUseCase(repo).execute()

        assert result[0]["id"] == 1
        assert result[0]["name"] == "admin"
        assert result[0]["description"] == "Administrator"
        assert "is_selected" in result[0]


class TestListRolesWithUser:
    def test_assigned_role_marked_is_selected(self):
        family = _make_entity(1, "family")
        lunchcare = _make_entity(2, "lunchcare")
        repo = _make_repo(roles=[family, lunchcare])

        mock_assoc = MagicMock()
        mock_assoc.role_id = 1

        with patch("app.infrastructure.user.orm.UserRoleAssociation") as mock_ura:
            mock_ura.query.filter_by.return_value.all.return_value = [mock_assoc]
            result = ListRolesUseCase(repo, user_id=5).execute()

        by_id = {item["id"]: item for item in result}
        assert by_id[1]["is_selected"] is True
        assert by_id[2]["is_selected"] is False

    def test_no_assigned_all_false(self):
        entities = [_make_entity(1, "family"), _make_entity(2, "lunchcare")]
        repo = _make_repo(roles=entities)

        with patch("app.infrastructure.user.orm.UserRoleAssociation") as mock_ura:
            mock_ura.query.filter_by.return_value.all.return_value = []
            result = ListRolesUseCase(repo, user_id=99).execute()

        assert all(item["is_selected"] is False for item in result)


class TestListRolesAdminAtEnd:
    def test_admin_moved_to_end(self):
        admin = _make_entity(1, "admin")
        family = _make_entity(2, "family")
        lunchcare = _make_entity(3, "lunchcare")
        # list_all returns admin first (alphabetical order)
        repo = _make_repo(roles=[admin, family, lunchcare])

        result = ListRolesUseCase(repo, user_id=None).execute()

        assert result[-1]["name"] == "admin"

    def test_no_admin_order_unchanged(self):
        family = _make_entity(2, "family")
        lunchcare = _make_entity(3, "lunchcare")
        repo = _make_repo(roles=[family, lunchcare])

        result = ListRolesUseCase(repo, user_id=None).execute()

        assert result[0]["name"] == "family"
        assert result[1]["name"] == "lunchcare"
