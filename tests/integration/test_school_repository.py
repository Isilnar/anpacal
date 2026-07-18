"""
Tests de integración: SQLAlchemySchoolRepository contra SQLite in-memory.

REQ-R03:
- test_save_creates_new_school
- test_save_updates_existing_school
- test_find_by_id_returns_school
- test_find_by_id_returns_none_when_not_found
- test_list_active_filters_by_status
- test_soft_delete_sets_status_0

REGLAS CRÍTICAS:
- SIN DELETE en fixtures
- SIN drop_all
- sqlalchemy_session inyectada desde fixture db
"""

import pytest

from app.domain.school.school import School
from app.infrastructure.school.repository import SQLAlchemySchoolRepository
from tests.factories.school_orm_factory import SchoolORMFactory


@pytest.fixture
def repo(app, db):
    """Repositorio con sesión real de SQLite in-memory."""
    with app.app_context():
        yield SQLAlchemySchoolRepository()


@pytest.fixture(autouse=True)
def setup_factory_session(app, db):
    """Inyecta la sesión in-memory en la factory. Sin DELETE."""
    with app.app_context():
        SchoolORMFactory._meta.sqlalchemy_session = db.session
        yield


class TestSaveCreatesNewSchool:
    def test_save_creates_new_school(self, repo, app):
        with app.app_context():
            school = School(name="Novo Colexio", address="Rúa Nova")
            saved = repo.save(school)

            assert saved.id is not None
            assert saved.name == "Novo Colexio"
            assert saved.address == "Rúa Nova"

    def test_save_assigns_id(self, repo, app):
        with app.app_context():
            school = School(name="Outro Colexio", address="Rúa Outra")
            saved = repo.save(school)
            assert isinstance(saved.id, int)
            assert saved.id > 0


class TestSaveUpdatesExistingSchool:
    def test_save_updates_existing_school(self, repo, app):
        with app.app_context():
            orm = SchoolORMFactory.create(name="Antes", address="Rúa A")

            school = School(id=orm.id, name="Despois", address="Rúa A")
            updated = repo.save(school)

            assert updated.id == orm.id
            assert updated.name == "Despois"


class TestGetById:
    def test_find_by_id_returns_school(self, repo, app):
        with app.app_context():
            orm = SchoolORMFactory.create(name="Colexio B", address="Rúa B")

            found = repo.get_by_id(orm.id)

            assert found is not None
            assert found.id == orm.id
            assert found.name == "Colexio B"

    def test_find_by_id_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.get_by_id(99999)
            assert result is None


class TestListActive:
    def test_list_active_filters_by_status(self, repo, app):
        with app.app_context():
            SchoolORMFactory.create(name="Activo1", address="Rúa 1", status=1)
            SchoolORMFactory.create(name="Activo2", address="Rúa 2", status=1)
            SchoolORMFactory.create(name="Inactivo", address="Rúa 3", status=0)

            activos = repo.list_active()
            nombres = [s.name for s in activos]

            assert "Activo1" in nombres
            assert "Activo2" in nombres
            assert "Inactivo" not in nombres


class TestSoftDelete:
    def test_soft_delete_sets_status_0(self, repo, app):
        with app.app_context():
            orm = SchoolORMFactory.create(name="Borrar", address="Rúa X", status=1)

            repo.soft_delete(orm.id)

            found = repo.get_by_id(orm.id)
            assert found is not None
            assert found.status == 0

    def test_soft_deleted_not_in_active_list(self, repo, app):
        with app.app_context():
            orm = SchoolORMFactory.create(name="BorrarActivo", address="Rúa Y", status=1)
            repo.soft_delete(orm.id)

            activos = repo.list_active()
            nombres = [s.name for s in activos]
            assert "BorrarActivo" not in nombres


class TestGetByNameAndAddress:
    def test_find_existing_school(self, repo, app):
        with app.app_context():
            SchoolORMFactory.create(name="Único", address="Rúa Única")

            found = repo.get_by_name_and_address("Único", "Rúa Única")
            assert found is not None
            assert found.name == "Único"

    def test_returns_none_when_not_found(self, repo, app):
        with app.app_context():
            result = repo.get_by_name_and_address("NoExiste", "Rúa NoExiste")
            assert result is None


class TestListAll:
    def test_list_all_returns_all_schools_regardless_of_status(self, repo, app):
        """list_all() returns all schools — active and inactive (lines 33-34)."""
        with app.app_context():
            SchoolORMFactory.create(name="ListAllActive", address="Rúa ListAll1", status=1)
            SchoolORMFactory.create(name="ListAllInactive", address="Rúa ListAll2", status=0)

            all_schools = repo.list_all()
            names = [s.name for s in all_schools]
            assert "ListAllActive" in names
            assert "ListAllInactive" in names


class TestListByIds:
    def test_list_by_ids_returns_only_matching(self, repo, app):
        """list_by_ids([ids]) returns only those schools (lines 37-40)."""
        with app.app_context():
            orm1 = SchoolORMFactory.create(name="ById1", address="Rúa ById1")
            orm2 = SchoolORMFactory.create(name="ById2", address="Rúa ById2")
            SchoolORMFactory.create(name="ByIdNotIncluded", address="Rúa Other")

            result = repo.list_by_ids([orm1.id, orm2.id])
            names = [s.name for s in result]
            assert "ById1" in names
            assert "ById2" in names
            assert "ByIdNotIncluded" not in names

    def test_list_by_ids_empty_returns_empty(self, repo, app):
        """list_by_ids([]) returns [] immediately (lines 37-38)."""
        with app.app_context():
            result = repo.list_by_ids([])
            assert result == []


class TestSaveNotFound:
    def test_save_with_unknown_id_raises_value_error(self, repo, app):
        """save(school) with non-existent id raises ValueError (line 66)."""
        import pytest

        from app.domain.school.school import School

        with app.app_context():
            school = School(id=999999, name="Ghost", address="Nowhere")
            with pytest.raises(ValueError, match="not found"):
                repo.save(school)


class TestSoftDeleteNotFound:
    def test_soft_delete_nonexistent_id_is_noop(self, repo, app):
        """soft_delete() with unknown id returns silently (line 80)."""
        with app.app_context():
            # Should NOT raise
            repo.soft_delete(999999)
