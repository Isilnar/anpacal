"""
GetUserUseCase — obtiene un usuario por id con PII desencriptada.

El mapper ya desencripta la PII en orm_to_domain(); el use case
simplemente delega en el repositorio que ya hace esa transformación.
"""

from app.domain.user.user import User

from .edit import UserNotFoundError


class GetUserUseCase:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, user_id: int) -> User:
        """
        Retorna User dominio con PII desencriptada.

        Raises:
            UserNotFoundError: si no existe user con ese id.
        """
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id={user_id} not found")
        return user
