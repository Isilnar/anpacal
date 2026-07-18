import factory

from app.domain.user.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    username = factory.Sequence(lambda n: f"user_{n}")
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    number_id = factory.Sequence(lambda n: f"12345{n:03d}A")
    address = factory.Faker("address")
    status = 1
    user_partner = ""
    ws_token = None
    roles = factory.LazyFunction(list)
