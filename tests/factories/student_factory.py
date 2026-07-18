import factory

from app.domain.student.student import Student


class StudentFactory(factory.Factory):
    class Meta:
        model = Student

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    school_id = 1
    classroom = factory.Sequence(lambda n: f"1-{n}A")
    number_id = factory.Sequence(lambda n: f"1234{n:04d}A")
    phone = factory.Faker("phone_number")
    email = factory.Faker("email")
    address = factory.Faker("address")
    allergies = ""
    status = 1
    childish = "no"
    brother_number = 0
    student_number = ""
    intolerance_ids = factory.LazyFunction(list)
