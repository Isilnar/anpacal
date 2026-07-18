"""
Tests unitarios: GetSchoolCourseUseCase.

REQ-SC03: GetSchoolCourseUseCase returns Optional[SchoolCourseEntity]
"""

from unittest.mock import MagicMock

import pytest

from app.application.school_course.get_school_course import GetSchoolCourseUseCase
from app.domain.school_course.entities import SchoolCourseEntity


class TestGetSchoolCourseUseCase:
    def test_found_returns_entity(self):
        """Scenario: Found — returns SchoolCourseEntity."""
        existing = SchoolCourseEntity(id=1, description="1º Primaria", status=1)
        repo = MagicMock()
        repo.get_by_id.return_value = existing

        result = GetSchoolCourseUseCase(repo, 1).execute()

        assert result is not None
        assert result.id == 1
        assert result.description == "1º Primaria"

    def test_not_found_returns_none(self):
        """Scenario: Not found — returns None (no exception)."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        result = GetSchoolCourseUseCase(repo, 99).execute()

        assert result is None

    def test_calls_repo_with_course_id(self):
        """Scenario: repo.get_by_id is called with the provided course_id."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        GetSchoolCourseUseCase(repo, 42).execute()

        repo.get_by_id.assert_called_once_with(42)

    def test_description_accessible_on_result(self):
        """Scenario: description field accessible for reports_routes fallback pattern."""
        existing = SchoolCourseEntity(id=5, description="3º ESO", status=1)
        repo = MagicMock()
        repo.get_by_id.return_value = existing

        result = GetSchoolCourseUseCase(repo, 5).execute()

        # Simulates: course.description if course else ""
        description = result.description if result else ""
        assert description == "3º ESO"

    def test_fallback_pattern_when_none(self):
        """Scenario: fallback pattern returns empty string when course not found."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        result = GetSchoolCourseUseCase(repo, 99).execute()

        # Simulates: course.description if course else ""
        description = result.description if result else ""
        assert description == ""
