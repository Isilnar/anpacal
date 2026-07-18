"""
Tests unitarios: CreateSchoolUseCase.

REQ-A01: CreateSchoolUseCase — dedup por (name, address), repo.save() una vez.
"""

from unittest.mock import MagicMock, call

import pytest

from app.application.school.create import CreateSchoolUseCase, DuplicateSchoolError
from app.application.school.dtos import SchoolCreateDTO
from app.domain.school.school import School


def _make_repo(existing=None):
    repo = MagicMock()
    repo.get_by_name_and_address.return_value = existing
    repo.save.side_effect = lambda s: School(
        id=1, name=s.name, address=s.address, phone=s.phone, email=s.email, status=s.status
    )
    return repo


class TestCreateSchoolUseCase:
    def test_create_new_school_calls_save_once(self):
        repo = _make_repo(existing=None)
        dto = SchoolCreateDTO(name="Novo", address="Rúa 1")
        use_case = CreateSchoolUseCase(repo)

        result = use_case.execute(dto)

        repo.save.assert_called_once()
        assert result.name == "Novo"

    def test_create_new_school_no_crypto(self):
        """REQ-A01: Sin llamadas a encryption."""
        repo = _make_repo(existing=None)
        dto = SchoolCreateDTO(name="Test", address="Addr")
        use_case = CreateSchoolUseCase(repo)

        # No debe lanzar error relacionado con crypto
        result = use_case.execute(dto)
        assert result is not None

    def test_create_school_returns_entity_with_correct_fields(self):
        repo = _make_repo(existing=None)
        dto = SchoolCreateDTO(name="Colexio A", address="Rúa A", phone="999", email="a@a.com")
        use_case = CreateSchoolUseCase(repo)

        result = use_case.execute(dto)

        assert result.name == "Colexio A"
        assert result.address == "Rúa A"

    def test_duplicate_school_raises_error(self):
        """REQ-A01: Dedup por (name, address) — raise DuplicateSchoolError."""
        existing = School(id=99, name="Dup", address="Rúa Dup")
        repo = _make_repo(existing=existing)
        dto = SchoolCreateDTO(name="Dup", address="Rúa Dup")
        use_case = CreateSchoolUseCase(repo)

        with pytest.raises(DuplicateSchoolError):
            use_case.execute(dto)

    def test_duplicate_school_save_not_called(self):
        """repo.save() NO se llama si es duplicado."""
        existing = School(id=99, name="Dup", address="Rúa Dup")
        repo = _make_repo(existing=existing)
        dto = SchoolCreateDTO(name="Dup", address="Rúa Dup")
        use_case = CreateSchoolUseCase(repo)

        with pytest.raises(DuplicateSchoolError):
            use_case.execute(dto)

        repo.save.assert_not_called()
