"""Application layer — User module exports."""

from .authenticate import AuthenticateUserUseCase, AuthenticationError
from .create import CreateUserUseCase, DuplicateUsernameError
from .delete import DeleteUserUseCase
from .dtos import AuthDTO, UserCreateDTO, UserEditDTO
from .edit import EditUserUseCase, UserNotFoundError
from .generate_token import GenerateTokenUseCase
from .get import GetUserUseCase
from .list_users import ListUsersUseCase

__all__ = [
    # DTOs
    "AuthDTO",
    "UserCreateDTO",
    "UserEditDTO",
    # Use cases
    "AuthenticateUserUseCase",
    "CreateUserUseCase",
    "EditUserUseCase",
    "DeleteUserUseCase",
    "GetUserUseCase",
    "ListUsersUseCase",
    "GenerateTokenUseCase",
    # Errors
    "AuthenticationError",
    "DuplicateUsernameError",
    "UserNotFoundError",
]
