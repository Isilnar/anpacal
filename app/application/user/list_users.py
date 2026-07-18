"""
ListUsersUseCase — retorna lista de usuarios activos (status=1).
"""

from app.domain.user.user import User


class ListUsersUseCase:
    def __init__(self, repository):
        self.repository = repository

    def execute(self) -> list[User]:
        """Retorna todos los usuarios con status=1."""
        return self.repository.list_active()
