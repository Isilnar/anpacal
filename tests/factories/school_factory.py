import factory

from app.domain.school.school import School


class SchoolFactory(factory.Factory):
    """Factory Boy para domain entity School — sin DB."""

    class Meta:
        model = School

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Colexio {n}")
    address = factory.Faker("address")
    phone = factory.Faker("phone_number")
    email = factory.Faker("email")
    status = 1
