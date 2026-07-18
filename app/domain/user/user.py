from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class User:
    username: str
    name: str
    surname: str
    id: int | None = None
    email: str = ""
    phone: str = ""
    number_id: str = ""
    address: str = ""
    status: int = 1
    user_partner: str = ""
    ws_token: str | None = None
    roles: list[str] = field(default_factory=list)
    hashed_password: str | None = None  # solo usado en creación; el repo lo setea en ORM

    def is_active(self) -> bool:
        return self.status == 1

    def get_fullname(self) -> str:
        return f"{self.name} {self.surname}"

    def get_fullname_reverse(self) -> str:
        return f"{self.surname}, {self.name}"

    def get_avatar_text(self) -> str:
        parts = []
        if self.name:
            parts.append(self.name[0].upper())
        if self.surname:
            parts.append(self.surname[0].upper())
        return "".join(parts)

    def has_role(self, role_name: str) -> bool:
        return role_name in self.roles

    def is_admin(self) -> bool:
        return self.has_role("admin")

    def is_family(self) -> bool:
        return self.has_role("family")
