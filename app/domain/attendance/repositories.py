"""
Attendance repositories — abstract interfaces (domain layer).

No SQLAlchemy, Flask, nor cryptography imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.domain.attendance.early_attendance import EarlyAttendance
from app.domain.attendance.lunch_attendance import LunchAttendance


class EarlyAttendanceRepository(ABC):
    @abstractmethod
    def find_by_id(self, attendance_id: int) -> EarlyAttendance | None:
        """Busca un registro de asistencia temprana por su PK."""
        ...

    @abstractmethod
    def search(
        self,
        student_id: int,
        user_student_ids: list[int],
        date_from: str,
        date_until: str,
    ) -> list[EarlyAttendance]:
        """
        Búsqueda multi-criterio con status=1 y rango de fechas.

        student_id=0 → no filtrar por alumno individual.
        user_student_ids vacío → no filtrar por usuarios.
        Si ambos se proporcionan, student_id tiene precedencia.
        """
        ...

    @abstractmethod
    def find_by_student_and_date(self, student_id: int, day: date) -> EarlyAttendance | None: ...

    @abstractmethod
    def list_by_school_and_date(self, school_id: int, day: date) -> list[EarlyAttendance]: ...

    @abstractmethod
    def list_by_student_ids_from_date(self, student_ids: list[int], from_date: date) -> list[EarlyAttendance]:
        """Return active records for student_ids where early_day >= from_date."""
        ...

    @abstractmethod
    def list_by_date_range(
        self,
        date_from: str,
        date_until: str,
        student_id: int = 0,
        type_filter: str | None = None,
    ) -> list[EarlyAttendance]:
        """
        Retorna registros en el rango [date_from, date_until].

        type_filter=None  → early_requested==1 OR early_plus_requested==1
        type_filter='early'      → solo early_requested=1, status=1
        type_filter='early_plus' → solo early_plus_requested=1, status=1
        student_id=0 → todos los alumnos; >0 → filtrar por alumno.
        """
        ...

    @abstractmethod
    def list_by_day(
        self,
        day: date,
        type_filter: str | None = None,
    ) -> list[EarlyAttendance]:
        """
        Retorna registros de un día exacto.

        type_filter=None       → early_requested==1 OR early_plus_requested==1
        type_filter='plus_only' → solo early_plus_requested=1
        Sin filtro de status.
        """
        ...

    @abstractmethod
    def save(self, attendance: EarlyAttendance) -> EarlyAttendance: ...

    @abstractmethod
    def delete(self, attendance_id: int) -> None:
        """Soft-delete: sets status=0."""
        ...


class LunchAttendanceRepository(ABC):
    @abstractmethod
    def find_by_id(self, attendance_id: int) -> LunchAttendance | None:
        """Busca un registro de comedor por su PK."""
        ...

    @abstractmethod
    def search(
        self,
        student_id: int,
        user_student_ids: list[int],
        date_from: str,
        date_until: str,
    ) -> list[LunchAttendance]:
        """
        Búsqueda multi-criterio con status=1 y rango de fechas.

        student_id=0 → no filtrar por alumno individual.
        user_student_ids vacío → no filtrar por usuarios.
        """
        ...

    @abstractmethod
    def find_by_student_and_date(self, student_id: int, day: date) -> LunchAttendance | None: ...

    @abstractmethod
    def list_by_school_and_date(self, school_id: int, day: date) -> list[LunchAttendance]: ...

    @abstractmethod
    def list_by_student_ids_from_date(self, student_ids: list[int], from_date: date) -> list[LunchAttendance]:
        """Return active records for student_ids where lunch_day >= from_date."""
        ...

    @abstractmethod
    def list_by_date_range(
        self,
        date_from: str,
        date_until: str,
        student_id: int = 0,
    ) -> list[LunchAttendance]:
        """
        Retorna registros con status=1, lunch_requested=1 en el rango dado.
        student_id=0 → todos; >0 → filtrar por alumno.
        """
        ...

    @abstractmethod
    def list_by_day(
        self,
        day: date,
        non_extra_only: bool = False,
    ) -> list[LunchAttendance]:
        """
        Retorna registros de un día exacto con lunch_requested=1.
        non_extra_only=False → todos; True → excluye extras (as_extra=1).
        Sin filtro de status.
        """
        ...

    @abstractmethod
    def save(self, attendance: LunchAttendance) -> LunchAttendance: ...

    @abstractmethod
    def delete(self, attendance_id: int) -> None:
        """Soft-delete: sets status=0."""
        ...
