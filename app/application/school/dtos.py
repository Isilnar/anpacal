from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SchoolCreateDTO:
    name: str
    address: str
    phone: str = ""
    email: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.address.strip():
            raise ValueError("address is required")
        if self.email and "@" not in self.email:
            raise ValueError("email is invalid")


@dataclass
class SchoolEditDTO:
    school_id: int
    name: str
    address: str
    phone: str = ""
    email: str = ""

    def __post_init__(self) -> None:
        if self.school_id <= 0:
            raise ValueError("school_id must be a positive integer")
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.address.strip():
            raise ValueError("address is required")
        if self.email and "@" not in self.email:
            raise ValueError("email is invalid")
