"""
GenerateTokenUseCase — genera y persiste un ws_token para el usuario.

El token se genera con SHA-512 usando el timestamp actual + username,
igual que el método update_token() del ORM original.
El use case genera el token, lo asigna al User dominio y llama repo.save().
"""

from datetime import datetime
from hashlib import sha512

from .edit import UserNotFoundError


class GenerateTokenUseCase:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, user_id: int) -> str:
        """
        Genera un nuevo ws_token y lo persiste.

        Returns:
            El nuevo ws_token generado.

        Raises:
            UserNotFoundError: si no existe user con ese id.
        """
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id={user_id} not found")

        # Generar token igual que ORM.update_token()
        now = datetime.now()
        st = now.strftime("%Y%m%d%H%M%S%f")
        st = f"{st}-{user.username}"
        token = sha512(st.encode("utf-8")).hexdigest()

        user.ws_token = token
        self.repository.save(user)

        return token
