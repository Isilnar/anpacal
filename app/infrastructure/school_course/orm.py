"""
SchoolCourseORM — ORM class defined directly here (infrastructure/school_course).

Ciclo D2: Class body inlined from models/school.py — app/models is no longer imported.
Class defined as SchoolCourses (original name), exported as SchoolCourseORM.
"""

from datetime import datetime

from app import db

__all__ = ["SchoolCourseORM"]


class SchoolCourses(db.Model):
    __tablename__ = "school_courses"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    description = db.Column(db.String())
    status = db.Column(db.Integer(), default=1)


# Export alias
SchoolCourseORM = SchoolCourses
