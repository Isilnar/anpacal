from datetime import datetime

import factory

from app.domain.menu.menu import Menu


class MenuFactory(factory.Factory):
    """Factory Boy para domain entity Menu — sin DB."""

    class Meta:
        model = Menu

    id = factory.Sequence(lambda n: n + 1)
    menu_link = factory.Sequence(lambda n: f"/static/menu/menu_{n}.json")
    status = 1
    created_at = factory.LazyFunction(datetime.now)
