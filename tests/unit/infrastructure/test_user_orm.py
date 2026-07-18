"""
Tests del modelo UserORM — usando app context (SQLite in-memory).

Verifica estructura del modelo sin necesitar una DB real poblada.
"""

import pytest
from flask_login import UserMixin

from app.infrastructure.user.orm import UserORM


def test_user_orm_has_user_mixin(app):
    assert issubclass(UserORM, UserMixin)


def test_user_orm_tablename_is_user(app):
    assert UserORM.__tablename__ == "user"


def test_user_orm_has_required_columns(app):
    columns = {c.key for c in UserORM.__table__.columns}
    required = {"id", "username", "email", "phone", "status", "name", "surname", "number_id"}
    assert required.issubset(columns)


def test_user_orm_id_is_primary_key(app):
    pk_cols = [c for c in UserORM.__table__.columns if c.primary_key]
    assert len(pk_cols) == 1
    assert pk_cols[0].key == "id"


def test_user_orm_username_is_unique(app):
    col = UserORM.__table__.columns["username"]
    assert col.unique is True
