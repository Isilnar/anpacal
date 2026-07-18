"""
Tests para validación __post_init__ de todos los DTOs.

Cubre los branches de ValueError en:
- app/application/holyday/dtos.py
- app/application/school/dtos.py
- app/application/student/dtos.py
- app/application/user/dtos.py
"""

from datetime import date

import pytest

# ---------------------------------------------------------------------------
# HolydayCreateDTO
# ---------------------------------------------------------------------------


class TestHolydayCreateDTO:
    def test_valid_construction(self):
        from app.application.holyday.dtos import HolydayCreateDTO

        dto = HolydayCreateDTO(holyday=date(2026, 1, 1))
        assert dto.holyday == date(2026, 1, 1)

    def test_raises_if_holyday_not_date(self):
        from app.application.holyday.dtos import HolydayCreateDTO

        with pytest.raises(ValueError, match="holyday must be a date"):
            HolydayCreateDTO(holyday="2026-01-01")


# ---------------------------------------------------------------------------
# HolydayEditDTO
# ---------------------------------------------------------------------------


class TestHolydayEditDTO:
    def test_valid_construction(self):
        from app.application.holyday.dtos import HolydayEditDTO

        dto = HolydayEditDTO(holyday_id=1, holyday=date(2026, 1, 1))
        assert dto.holyday_id == 1

    def test_raises_if_holyday_id_zero(self):
        from app.application.holyday.dtos import HolydayEditDTO

        with pytest.raises(ValueError, match="holyday_id must be a positive integer"):
            HolydayEditDTO(holyday_id=0, holyday=date(2026, 1, 1))

    def test_raises_if_holyday_id_negative(self):
        from app.application.holyday.dtos import HolydayEditDTO

        with pytest.raises(ValueError, match="holyday_id must be a positive integer"):
            HolydayEditDTO(holyday_id=-1, holyday=date(2026, 1, 1))

    def test_raises_if_holyday_not_date(self):
        from app.application.holyday.dtos import HolydayEditDTO

        with pytest.raises(ValueError, match="holyday must be a date"):
            HolydayEditDTO(holyday_id=1, holyday="not-a-date")


# ---------------------------------------------------------------------------
# SchoolCreateDTO
# ---------------------------------------------------------------------------


class TestSchoolCreateDTO:
    def test_valid_construction(self):
        from app.application.school.dtos import SchoolCreateDTO

        dto = SchoolCreateDTO(name="CEIP Example", address="Rúa Maior 1")
        assert dto.name == "CEIP Example"

    def test_raises_if_name_empty(self):
        from app.application.school.dtos import SchoolCreateDTO

        with pytest.raises(ValueError, match="name is required"):
            SchoolCreateDTO(name="   ", address="Rúa Maior 1")

    def test_raises_if_address_empty(self):
        from app.application.school.dtos import SchoolCreateDTO

        with pytest.raises(ValueError, match="address is required"):
            SchoolCreateDTO(name="CEIP", address="   ")

    def test_raises_if_email_invalid(self):
        from app.application.school.dtos import SchoolCreateDTO

        with pytest.raises(ValueError, match="email is invalid"):
            SchoolCreateDTO(name="CEIP", address="Rúa 1", email="not-an-email")

    def test_valid_with_email(self):
        from app.application.school.dtos import SchoolCreateDTO

        dto = SchoolCreateDTO(name="CEIP", address="Rúa 1", email="test@example.com")
        assert dto.email == "test@example.com"


# ---------------------------------------------------------------------------
# SchoolEditDTO
# ---------------------------------------------------------------------------


class TestSchoolEditDTO:
    def test_valid_construction(self):
        from app.application.school.dtos import SchoolEditDTO

        dto = SchoolEditDTO(school_id=1, name="CEIP Example", address="Rúa Maior 1")
        assert dto.school_id == 1

    def test_raises_if_school_id_zero(self):
        from app.application.school.dtos import SchoolEditDTO

        with pytest.raises(ValueError, match="school_id must be a positive integer"):
            SchoolEditDTO(school_id=0, name="CEIP", address="Rúa 1")

    def test_raises_if_school_id_negative(self):
        from app.application.school.dtos import SchoolEditDTO

        with pytest.raises(ValueError, match="school_id must be a positive integer"):
            SchoolEditDTO(school_id=-5, name="CEIP", address="Rúa 1")

    def test_raises_if_name_empty(self):
        from app.application.school.dtos import SchoolEditDTO

        with pytest.raises(ValueError, match="name is required"):
            SchoolEditDTO(school_id=1, name="", address="Rúa 1")

    def test_raises_if_address_empty(self):
        from app.application.school.dtos import SchoolEditDTO

        with pytest.raises(ValueError, match="address is required"):
            SchoolEditDTO(school_id=1, name="CEIP", address="")

    def test_raises_if_email_invalid(self):
        from app.application.school.dtos import SchoolEditDTO

        with pytest.raises(ValueError, match="email is invalid"):
            SchoolEditDTO(school_id=1, name="CEIP", address="Rúa 1", email="bad-email")


# ---------------------------------------------------------------------------
# StudentCreateDTO
# ---------------------------------------------------------------------------


class TestStudentCreateDTO:
    def test_valid_construction(self):
        from app.application.student.dtos import StudentCreateDTO

        dto = StudentCreateDTO(name="Ana", surname="García", school_id=1)
        assert dto.name == "Ana"

    def test_raises_if_name_empty(self):
        from app.application.student.dtos import StudentCreateDTO

        with pytest.raises(ValueError, match="name is required"):
            StudentCreateDTO(name="  ", surname="García", school_id=1)

    def test_raises_if_surname_empty(self):
        from app.application.student.dtos import StudentCreateDTO

        with pytest.raises(ValueError, match="surname is required"):
            StudentCreateDTO(name="Ana", surname="  ", school_id=1)

    def test_raises_if_school_id_zero(self):
        from app.application.student.dtos import StudentCreateDTO

        with pytest.raises(ValueError, match="school_id must be a positive integer"):
            StudentCreateDTO(name="Ana", surname="García", school_id=0)

    def test_raises_if_email_invalid(self):
        from app.application.student.dtos import StudentCreateDTO

        with pytest.raises(ValueError, match="email is invalid"):
            StudentCreateDTO(name="Ana", surname="García", school_id=1, email="not-email")

    def test_raises_if_brother_number_negative(self):
        from app.application.student.dtos import StudentCreateDTO

        with pytest.raises(ValueError, match="brother_number cannot be negative"):
            StudentCreateDTO(name="Ana", surname="García", school_id=1, brother_number=-1)


# ---------------------------------------------------------------------------
# StudentEditDTO
# ---------------------------------------------------------------------------


class TestStudentEditDTO:
    def test_valid_construction(self):
        from app.application.student.dtos import StudentEditDTO

        dto = StudentEditDTO(student_id=1, name="Ana", surname="García", school_id=1)
        assert dto.student_id == 1

    def test_raises_if_student_id_zero(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="student_id must be a positive integer"):
            StudentEditDTO(student_id=0, name="Ana", surname="García", school_id=1)

    def test_raises_if_student_id_negative(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="student_id must be a positive integer"):
            StudentEditDTO(student_id=-1, name="Ana", surname="García", school_id=1)

    def test_raises_if_name_empty(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="name is required"):
            StudentEditDTO(student_id=1, name="", surname="García", school_id=1)

    def test_raises_if_surname_empty(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="surname is required"):
            StudentEditDTO(student_id=1, name="Ana", surname="", school_id=1)

    def test_raises_if_school_id_zero(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="school_id must be a positive integer"):
            StudentEditDTO(student_id=1, name="Ana", surname="García", school_id=0)

    def test_raises_if_email_invalid(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="email is invalid"):
            StudentEditDTO(student_id=1, name="Ana", surname="García", school_id=1, email="bad")

    def test_raises_if_brother_number_negative(self):
        from app.application.student.dtos import StudentEditDTO

        with pytest.raises(ValueError, match="brother_number cannot be negative"):
            StudentEditDTO(student_id=1, name="Ana", surname="García", school_id=1, brother_number=-2)


# ---------------------------------------------------------------------------
# AuthDTO
# ---------------------------------------------------------------------------


class TestAuthDTO:
    def test_valid_construction(self):
        from app.application.user.dtos import AuthDTO

        dto = AuthDTO(username="admin", password="secret")
        assert dto.username == "admin"

    def test_raises_if_username_empty(self):
        from app.application.user.dtos import AuthDTO

        with pytest.raises(ValueError, match="username is required"):
            AuthDTO(username="  ", password="secret")

    def test_raises_if_password_empty(self):
        from app.application.user.dtos import AuthDTO

        with pytest.raises(ValueError, match="password is required"):
            AuthDTO(username="admin", password="")


# ---------------------------------------------------------------------------
# UserCreateDTO
# ---------------------------------------------------------------------------


class TestUserCreateDTO:
    def _make(self, **kwargs):
        from app.application.user.dtos import UserCreateDTO

        defaults = dict(
            username="jdoe",
            name="John",
            surname="Doe",
            email="jdoe@example.com",
            phone="600000000",
            number_id="12345678A",
            address="Rúa 1",
            password="secret",
        )
        defaults.update(kwargs)
        return UserCreateDTO(**defaults)

    def test_valid_construction(self):
        dto = self._make()
        assert dto.username == "jdoe"

    def test_raises_if_username_empty(self):
        with pytest.raises(ValueError, match="username is required"):
            self._make(username="   ")

    def test_raises_if_name_empty(self):
        with pytest.raises(ValueError, match="name is required"):
            self._make(name="")

    def test_raises_if_surname_empty(self):
        with pytest.raises(ValueError, match="surname is required"):
            self._make(surname="")

    def test_raises_if_password_empty(self):
        with pytest.raises(ValueError, match="password is required"):
            self._make(password="")

    def test_raises_if_email_invalid(self):
        with pytest.raises(ValueError, match="email is invalid"):
            self._make(email="not-an-email")

    def test_valid_with_empty_email(self):
        dto = self._make(email="")
        assert dto.email == ""


# ---------------------------------------------------------------------------
# UserEditDTO
# ---------------------------------------------------------------------------


class TestUserEditDTO:
    def _make(self, **kwargs):
        from app.application.user.dtos import UserEditDTO

        defaults = dict(
            user_id=1,
            username="testuser",
            name="John",
            surname="Doe",
            email="jdoe@example.com",
            phone="600000000",
            number_id="12345678A",
            address="Rúa 1",
        )
        defaults.update(kwargs)
        return UserEditDTO(**defaults)

    def test_valid_construction(self):
        dto = self._make()
        assert dto.user_id == 1

    def test_raises_if_user_id_zero(self):
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            self._make(user_id=0)

    def test_raises_if_user_id_negative(self):
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            self._make(user_id=-1)

    def test_raises_if_name_empty(self):
        with pytest.raises(ValueError, match="name is required"):
            self._make(name="  ")

    def test_raises_if_surname_empty(self):
        with pytest.raises(ValueError, match="surname is required"):
            self._make(surname="")

    def test_raises_if_email_invalid(self):
        with pytest.raises(ValueError, match="email is invalid"):
            self._make(email="bad-email")
