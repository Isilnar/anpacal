"""
CreateHolydayUseCase — crea un nuevo holyday.

Flujo:
1. Verificar dedup por fecha — no se permiten fechas duplicadas.
2. Construir Holyday dominio con los datos del DTO.
3. repo.save(holyday) — persiste en un solo commit.
4. Retornar Holyday creado.

Sin CryptoService: Holyday no tiene campos PII.
"""

from __future__ import annotations

from app.domain.holyday.holyday import Holyday
from app.domain.holyday.repositories import HolydayRepository

from .dtos import HolydayCreateDTO


class DuplicateHolydayError(Exception):
    pass


class CreateHolydayUseCase:
    def __init__(self, repo: HolydayRepository):
        self.repo = repo

    def execute(self, dto: HolydayCreateDTO) -> Holyday:
        # 1. Verificar duplicado por fecha
        existing = self.repo.find_by_date(dto.holyday)
        if existing is not None:
            raise DuplicateHolydayError(f"Holyday on '{dto.holyday}' already exists")

        # 2. Construir dominio (sin id — save lo asignará)
        holyday = Holyday(holyday=dto.holyday, status=1)

        # 3. Persistir
        return self.repo.save(holyday)
