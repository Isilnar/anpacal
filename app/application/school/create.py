"""
CreateSchoolUseCase — crea un nuevo school.

Flujo:
1. Verificar dedup por (name, address) — no se permiten duplicados exactos.
2. Construir School dominio con los datos del DTO.
3. repo.save(school) — persiste en un solo commit.
4. Retornar School creado.

Sin CryptoService: School no tiene campos PII.
"""

from __future__ import annotations

from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School

from .dtos import SchoolCreateDTO


class DuplicateSchoolError(Exception):
    pass


class CreateSchoolUseCase:
    def __init__(self, repo: SchoolRepository):
        self.repo = repo

    def execute(self, dto: SchoolCreateDTO) -> School:
        # 1. Verificar duplicado por (name, address)
        existing = self.repo.get_by_name_and_address(dto.name, dto.address)
        if existing is not None:
            raise DuplicateSchoolError(f"School '{dto.name}' at '{dto.address}' already exists")

        # 2. Construir School dominio (sin id — save lo asignará)
        school = School(
            name=dto.name,
            address=dto.address,
            phone=dto.phone,
            email=dto.email,
            status=1,
        )

        # 3. Persistir
        return self.repo.save(school)
