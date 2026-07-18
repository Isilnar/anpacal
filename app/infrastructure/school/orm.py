"""
SchoolORM — ORM class defined directly here (infrastructure/school).

Ciclo D2: Class body inlined from models/school.py — app/models is no longer imported.
Class defined as School (for SQLAlchemy string-relationship resolution),
exported as SchoolORM for infrastructure naming convention.
"""

from datetime import datetime

from app import db

__all__ = ["SchoolORM"]


class School(db.Model):
    __tablename__ = "school"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    name = db.Column(db.String(100))
    address = db.Column(db.String(300))
    phone = db.Column(db.String(13))
    email = db.Column(db.String(100))
    status = db.Column(db.Integer(), default=1)

    students = db.relationship("Student", backref="school", order_by="Student.id")

    users = db.relationship("UserSchoolAssociation", back_populates="school")

    def get_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "status": self.status,
        }

        return data


# Export alias
SchoolORM = School
