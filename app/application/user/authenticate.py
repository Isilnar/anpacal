"""
AuthenticateUserUseCase — valida credenciales de un usuario.

Decisión de diseño (ver design.md):
    check_password() usa bcrypt y está en UserORM (Flask-Login adapter).
    El use case no puede usar el User dominio para verificar el password
    porque el dominio no sabe de bcrypt.

    Solución adoptada: el repositorio expone get_orm_by_username() —
    un método adicional que retorna UserORM solo para este use case.
    El dominio nunca importa UserORM; solo el use case conoce la interfaz
    extendida del repositorio concreto.

    El use case recibe el repositorio como `SQLAlchemyUserRepository`
    (o cualquier objeto que tenga `get_orm_by_username` + `find_by_username`).
    El adapter auth_routes.py construye las dependencias.
"""

from app.domain.user.user import User


class AuthenticationError(Exception):
    """Se lanza cuando las credenciales son inválidas o el usuario está inactivo."""

    pass


class AuthenticateUserUseCase:
    def __init__(self, repository):
        """
        repository: SQLAlchemyUserRepository (o compatible).
        Debe tener find_by_username() y get_orm_by_username().
        """
        self.repository = repository

    def execute(self, username: str, password: str) -> User:
        """
        Valida credenciales y retorna User dominio.

        Raises:
            AuthenticationError: si el username no existe, la contraseña es
                incorrecta, o el usuario está inactivo (status=0).
        """
        # Primero verificamos contraseña usando el ORM (que tiene check_password + bcrypt)
        orm_user = self.repository.get_orm_by_username(username)
        if orm_user is None:
            raise AuthenticationError("Invalid credentials")

        if not orm_user.check_password(password):
            raise AuthenticationError("Invalid credentials")

        # check_password ya verifica status=0 (retorna 0 si inactivo)
        if orm_user.status == 0:
            raise AuthenticationError("User is inactive")

        # Retornar el User dominio (con PII desencriptada)
        user = self.repository.find_by_username(username)
        if user is None:
            raise AuthenticationError("Invalid credentials")

        return user
