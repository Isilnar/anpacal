"""
Tests unitarios del dominio School.

REQ-D01: SchoolEntity como dataclass pura sin imports de framework.
REQ-D02: SchoolRepository ABC — enforce abstractmethod.
"""

import pytest

from app.domain.school.repositories import SchoolRepository
from app.domain.school.school import School

# ---------------------------------------------------------------------------
# REQ-D01: SchoolEntity
# ---------------------------------------------------------------------------


class TestSchoolDataclass:
    def test_construct_valid_school(self):
        s = School(name="Colexio A", address="Rúa 1")
        assert s.name == "Colexio A"
        assert s.address == "Rúa 1"
        assert s.status == 1
        assert s.id is None

    def test_no_framework_attributes(self):
        s = School(name="X", address="Y")
        assert not hasattr(s, "_sa_instance_state")
        assert not hasattr(s, "is_authenticated")

    def test_is_active_true_when_status_1(self):
        s = School(name="X", address="Y", status=1)
        assert s.is_active() is True

    def test_is_active_false_when_status_0(self):
        s = School(name="X", address="Y", status=0)
        assert s.is_active() is False

    def test_get_dict_contains_all_fields(self):
        s = School(id=5, name="Test", address="Addr", phone="123", email="a@b.com", status=1)
        d = s.get_dict()
        assert d["id"] == 5
        assert d["name"] == "Test"
        assert d["address"] == "Addr"
        assert d["phone"] == "123"
        assert d["email"] == "a@b.com"
        assert d["status"] == 1

    def test_default_phone_and_email_empty(self):
        s = School(name="X", address="Y")
        assert s.phone == ""
        assert s.email == ""


# ---------------------------------------------------------------------------
# REQ-D02: SchoolRepository ABC
# ---------------------------------------------------------------------------


class TestSchoolRepositoryABC:
    def test_abstract_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            SchoolRepository()  # type: ignore

    def test_concrete_subclass_valid(self):
        class ConcreteRepo(SchoolRepository):
            def get_by_id(self, school_id):
                return None

            def get_by_name_and_address(self, name, address):
                return None

            def list_active(self):
                return []

            def list_all(self):
                return []

            def list_by_ids(self, ids):
                return []

            def list_with_selection(self, user_id):
                return []

            def save(self, school):
                return school

            def soft_delete(self, school_id):
                pass

        repo = ConcreteRepo()
        assert repo is not None

    def test_incomplete_subclass_raises(self):
        class IncompleteRepo(SchoolRepository):
            def get_by_id(self, school_id):
                return None

            # missing the other 4 methods

        with pytest.raises(TypeError):
            IncompleteRepo()  # type: ignore
