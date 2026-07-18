"""
HolydayFactory — Factory Boy para domain entity Holyday — sin DB.
"""

from datetime import date

import factory

from app.domain.holyday.holyday import Holyday


class HolydayFactory(factory.Factory):
    """Factory Boy para domain entity Holyday — sin DB."""

    class Meta:
        model = Holyday

    id = factory.Sequence(lambda n: n + 1)
    holyday = factory.Sequence(lambda n: date(2026, 1, 1).replace(day=min(n % 28 + 1, 28)))
    status = 1
    created_at = None
