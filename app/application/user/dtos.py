"""
DTOs (Data Transfer Objects) para el módulo User.

Dataclasses con validación básica en __post_init__.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AuthDTO:
    username: str
    password: str

    def __post_init__(self) -> None:
        if not self.username.strip():
            raise ValueError("username is required")
        if not self.password:
            raise ValueError("password is required")


@dataclass
class UserCreateDTO:
    username: str
    name: str
    surname: str
    email: str
    phone: str
    number_id: str
    address: str
    password: str
    user_partner: str = ""
    role_ids: list[int] = field(default_factory=list)
    school_ids: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.username.strip():
            raise ValueError("username is required")
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.surname.strip():
            raise ValueError("surname is required")
        if not self.password:
            raise ValueError("password is required")
        if self.email and "@" not in self.email:
            raise ValueError("email is invalid")


@dataclass
class UserEditDTO:
    user_id: int
    username: str
    name: str
    surname: str
    email: str
    phone: str
    number_id: str
    address: str
    user_partner: str = ""
    new_password: str | None = None
    role_ids: list[int] = field(default_factory=list)
    school_ids: list[int] = field(default_factory=list)
    student_ids: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        if not self.username.strip():
            raise ValueError("username is required")
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.surname.strip():
            raise ValueError("surname is required")
        if self.email and "@" not in self.email:
            raise ValueError("email is invalid")
