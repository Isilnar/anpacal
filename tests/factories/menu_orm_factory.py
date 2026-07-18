"""
MenuORMFactory — Factory Boy + SQLAlchemy para tests de integración.

Uso en tests:
    MenuORMFactory._meta.sqlalchemy_session = db.session
    menu_orm = MenuORMFactory.create(menu_link="/static/menu/menu.json")
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.infrastructure.menu.orm import MenuORM


class MenuORMFactory(SQLAlchemyModelFactory):
    class Meta:
        model = MenuORM
        sqlalchemy_session = None  # se setea en el test/fixture
        sqlalchemy_session_persistence = "commit"

    menu_link = factory.Sequence(lambda n: f"/static/menu/menu_{n}.json")
    status = 1
