"""
DietIntoleranceORM and StudentIntoleranceORM — infrastructure/intolerance.

Ciclo D2: DietIntolerance class body inlined from models/student.py — app/models is no longer imported.
StudentIntoleranceORM re-exported from infrastructure/student/orm.py.
"""

from datetime import datetime

from app import db
from app.infrastructure.student.orm import StudentIntoleranceORM  # noqa: F401

__all__ = ["DietIntoleranceORM", "StudentIntoleranceORM"]


class DietIntolerance(db.Model):
    __tablename__ = "diet_intolerance"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    description = db.Column(db.String())
    status = db.Column(db.Integer(), default=1)
    students = db.relationship("StudentIntolerance", back_populates="intolerance")


# Export alias
DietIntoleranceORM = DietIntolerance
