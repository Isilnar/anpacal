"""
ListRolesUseCase — lista todos los roles con flag de selección.

Dado un user_id opcional, marca como is_selected los roles que el usuario tiene asignados.
Output: list[dict] con claves {id, name, description, is_selected: bool}.

El rol "admin" se mueve al final de la lista (preserva comportamiento original).
"""

from __future__ import annotations

from app.domain.role.repositories import RoleRepository


class ListRolesUseCase:
    def __init__(self, repo: RoleRepository, user_id: int | None = None):
        self.repo = repo
        self.user_id = user_id

    def execute(self) -> list[dict]:
        all_roles = self.repo.list_all()

        assigned_ids: set[int] = set()
        if self.user_id is not None:
            from app.infrastructure.user.orm import UserRoleAssociation

            assocs = UserRoleAssociation.query.filter_by(user_id=self.user_id).all()
            assigned_ids = {a.role_id for a in assocs}

        result = [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "is_selected": r.id in assigned_ids,
            }
            for r in all_roles
        ]

        # Move admin to end (preserve original behavior)
        admin = next((item for item in result if item.get("name") == "admin"), None)
        if admin is not None:
            result.remove(admin)
            result.append(admin)

        return result
