from abc import ABC, abstractmethod

from .student import Student


class StudentRepository(ABC):
    @abstractmethod
    def get_by_id(self, student_id: int) -> Student | None: ...

    @abstractmethod
    def get_by_number_id_hash_and_school(self, nid_hash: str, school_id: int) -> Student | None: ...

    @abstractmethod
    def list_active(self) -> list[Student]: ...

    @abstractmethod
    def list_active_with_school(self) -> list[Student]: ...

    @abstractmethod
    def get_associations_for_user(self, user_id: int) -> list[int]: ...

    @abstractmethod
    def save(self, student: Student) -> Student: ...

    @abstractmethod
    def soft_delete(self, student_id: int) -> None: ...

    @abstractmethod
    def sync_intolerances(self, student_id: int, intolerance_ids: list[int]) -> None: ...
