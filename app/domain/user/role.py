from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    id: int
    name: str

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Role):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)
