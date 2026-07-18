from abc import ABC, abstractmethod

from .user import User


class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def find_by_email_hash(self, email_hash: str) -> User | None: ...

    @abstractmethod
    def find_by_number_id_hash(self, number_id_hash: str) -> User | None: ...

    @abstractmethod
    def list_active(self) -> list[User]: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...

    @abstractmethod
    def get_partner_flag(self, student_id: int) -> bool:
        """
        Retorna True si TODOS los usuarios asociados al alumno son socios
        (user_partner == 'on').  Retorna False si alguno no es socio.
        Si el alumno no tiene usuarios asociados, retorna True (partner por defecto).
        """
        ...

    @abstractmethod
    def get_student_ids_by_user(self, user_id: int) -> list[int]:
        """Retorna los student_ids asociados a un usuario via UserStudentAssociation."""
        ...
