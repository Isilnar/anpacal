from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Student:
    name: str
    surname: str
    school_id: int
    id: int | None = None
    created_at: str | None = None
    classroom: str = ""
    number_id: str = ""  # decrypted in domain
    number_id_hash: str = ""
    childish: str = ""
    brother_number: int = 0
    student_number: str = ""
    phone: str = ""  # decrypted in domain
    email: str = ""  # decrypted in domain
    address: str = ""  # decrypted in domain
    allergies: str = ""
    status: int = 1
    intolerance_ids: list[int] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.status == 1

    def get_fullname(self) -> str:
        return f"{self.name} {self.surname}"

    def get_fullname_reverse(self) -> str:
        return f"{self.surname}, {self.name}"


@dataclass
class StudentWithAssociation:
    student: Student
    associated: bool
