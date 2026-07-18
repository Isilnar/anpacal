"""
Student ORM classes defined directly here (infrastructure/student).

Ciclo D2: Class bodies inlined from models/student.py — app/models is no longer imported.
Classes are defined with their original names for SQLAlchemy string-relationship resolution,
then exported under the ORM naming convention.
"""

from datetime import datetime

from app import db

__all__ = ["StudentORM", "StudentIntoleranceORM", "StudentLunch", "StudentEarly"]


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    school_id = db.Column(db.Integer(), db.ForeignKey("school.id"))
    classroom = db.Column(db.String(25))
    number_id = db.Column(db.String(120))
    number_id_hash = db.Column(db.String(64))
    childish = db.Column(db.String(2))
    brother_number = db.Column(db.Integer())
    student_number = db.Column(db.String(12))
    phone = db.Column(db.String(120))
    email = db.Column(db.String(250))
    address = db.Column(db.String(400))
    allergies = db.Column(db.String(300))
    status = db.Column(db.Integer(), default=1)

    students_lunch = db.relationship("StudentLunch", backref="student", order_by="StudentLunch.id")

    students_early = db.relationship("StudentEarly", backref="student", order_by="StudentEarly.id")

    users = db.relationship("UserStudentAssociation", back_populates="student")

    intolerances = db.relationship("StudentIntolerance", back_populates="student")

    def get_fullname(self):
        fullname = ""
        if self.name is not None and len(self.name) > 0:
            fullname = f"{self.name}"
        if self.surname is not None and len(self.surname) > 0:
            if len(fullname) > 0:
                fullname = f"{fullname} {self.surname}"
            else:
                fullname = f"{self.surname}"

        return fullname

    def get_fullname_reverse(self):
        fullname = ""
        if self.name is not None and len(self.name) > 0:
            fullname = f"{self.name}"
        if self.surname is not None and len(self.surname) > 0:
            if len(fullname) > 0:
                fullname = f"{self.surname}, {fullname}"
            else:
                fullname = f"{self.surname}"

        return fullname


# Export alias
StudentORM = Student


class StudentIntolerance(db.Model):
    __tablename__ = "student_intolerance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer(), db.ForeignKey("student.id"))
    intolerance_id = db.Column(db.Integer(), db.ForeignKey("diet_intolerance.id"))
    student = db.relationship("Student", back_populates="intolerances")
    intolerance = db.relationship("DietIntolerance", back_populates="students")


# Export alias
StudentIntoleranceORM = StudentIntolerance


class StudentLunch(db.Model):
    __tablename__ = "student_lunch"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    lunch_day = db.Column(db.DateTime())
    lunch_requested = db.Column(db.Integer())
    user_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer(), db.ForeignKey("student.id"))
    status = db.Column(db.Integer(), default=1)
    modify_user_id = db.Column(db.Integer())
    as_extra = db.Column(db.Integer())
    not_come = db.Column(db.Integer())
    modify_notes = db.Column(db.String())
    modify_date = db.Column(db.DateTime())


class StudentEarly(db.Model):
    __tablename__ = "student_early"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    early_day = db.Column(db.DateTime())
    early_requested = db.Column(db.Integer)
    early_plus_requested = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer(), db.ForeignKey("student.id"))
    status = db.Column(db.Integer(), default=1)
    modify_user_id = db.Column(db.Integer())
    as_extra = db.Column(db.Integer())
    not_come = db.Column(db.Integer())
    modify_notes = db.Column(db.String())
    modify_date = db.Column(db.DateTime())
