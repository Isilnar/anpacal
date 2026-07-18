"""
GetIntolerancesStringUseCase — retorna las descripciones de intolerancias como texto.

Devuelve un string con las descripciones unidas por ", " ordenadas alfabéticamente.
Retorna "" cuando el alumno no tiene intolerancias asignadas.
No accede a ORM ni DB directamente — delega al repositorio.
"""

from __future__ import annotations

from app.domain.intolerance.repositories import DietIntoleranceRepository


class GetIntolerancesStringUseCase:
    def __init__(self, repo: DietIntoleranceRepository):
        self.repo = repo

    def execute(self, student_id: int) -> str:
        return self.repo.get_string_for_student(student_id)
