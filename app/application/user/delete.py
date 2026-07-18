"""
DeleteUserUseCase — soft-delete de un usuario (status=0).

No elimina físicamente el registro de la base de datos.
Delega en repository.delete() que implementa el soft-delete.
"""

from .edit import UserNotFoundError


class DeleteUserUseCase:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, user_id: int) -> None:
        """
        Soft-delete: establece status=0 en el usuario.

        Raises:
            UserNotFoundError: si no existe user con ese id.
        """
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id={user_id} not found")

        self.repository.delete(user_id)
