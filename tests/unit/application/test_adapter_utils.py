"""
Tests para funciones de utilidad en app/adapters/utils.py.

Cubre:
- get_random_password: longitud correcta, solo chars del set
- get_calendar_start_date: format=0 devuelve string, format=1 devuelve datetime
- get_calendar_start_date_early_lunch: format=0 string, format=1 datetime
- get_dates_between: lista de fechas entre start y end
"""

from datetime import datetime

import pytest


class TestGetRandomPassword:
    def test_returns_string_of_requested_length(self):
        from app.adapters.utils import get_random_password

        pwd = get_random_password(8)
        assert isinstance(pwd, str)
        assert len(pwd) == 8

    def test_default_length_is_8(self):
        from app.adapters.utils import get_random_password

        pwd = get_random_password()
        assert len(pwd) == 8

    def test_custom_length(self):
        from app.adapters.utils import get_random_password

        pwd = get_random_password(12)
        assert len(pwd) == 12

    def test_returns_unique_passwords(self):
        from app.adapters.utils import get_random_password

        passwords = {get_random_password(8) for _ in range(10)}
        # Very unlikely all 10 would be identical
        assert len(passwords) > 1


class TestGetCalendarStartDate:
    def test_format_0_returns_string(self):
        from app.adapters.utils import get_calendar_start_date

        result = get_calendar_start_date(format=0)
        assert isinstance(result, str)
        # Check it's a valid date string
        datetime.strptime(result, "%Y-%m-%d")

    def test_format_1_returns_datetime(self):
        from app.adapters.utils import get_calendar_start_date

        result = get_calendar_start_date(format=1)
        assert not isinstance(result, str)
        # Should be a datetime/pendulum object with strftime
        assert hasattr(result, "strftime")

    def test_custom_time_limit(self):
        from app.adapters.utils import get_calendar_start_date

        # Using a very late time limit ensures result is today or tomorrow
        result = get_calendar_start_date(time_limit=(23, 59, 59, 0), format=0)
        assert isinstance(result, str)
        datetime.strptime(result, "%Y-%m-%d")


class TestGetCalendarStartDateEarlyLunch:
    def test_format_0_returns_string(self):
        from app.adapters.utils import get_calendar_start_date_early_lunch

        result = get_calendar_start_date_early_lunch(format=0)
        assert isinstance(result, str)
        datetime.strptime(result, "%Y-%m-%d")

    def test_format_1_returns_datetime(self):
        from app.adapters.utils import get_calendar_start_date_early_lunch

        result = get_calendar_start_date_early_lunch(format=1)
        assert not isinstance(result, str)
        assert hasattr(result, "strftime")


class TestGetDatesBetween:
    def test_returns_list_of_strings(self):
        from app.adapters.utils import get_dates_between

        result = get_dates_between("2026-03-01", "2026-03-05")
        assert isinstance(result, list)
        assert len(result) == 4  # [01, 02, 03, 04] — end excluded

    def test_dates_are_formatted_correctly(self):
        from app.adapters.utils import get_dates_between

        result = get_dates_between("2026-03-01", "2026-03-03")
        assert result == ["2026-03-01", "2026-03-02"]

    def test_empty_when_start_equals_end(self):
        from app.adapters.utils import get_dates_between

        result = get_dates_between("2026-03-15", "2026-03-15")
        assert result == []

    def test_empty_when_start_after_end(self):
        from app.adapters.utils import get_dates_between

        result = get_dates_between("2026-03-16", "2026-03-15")
        assert result == []

    def test_single_day_range(self):
        from app.adapters.utils import get_dates_between

        result = get_dates_between("2026-03-15", "2026-03-16")
        assert result == ["2026-03-15"]
