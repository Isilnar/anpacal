"""
HolydayORM — ORM class defined directly here (infrastructure/holyday).

Ciclo D2: Class body inlined from models/holydays.py — app/models is no longer imported.
Class defined as Holydays (original name), exported as HolydayORM.
"""

from datetime import datetime

from app import db

__all__ = ["HolydayORM"]


class Holydays(db.Model):
    __table_name__ = "holydays"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    holyday = db.Column(db.Date())
    status = db.Column(db.Integer(), default=1)

    def get_dict(self):
        res = {
            "id": self.id,
            "holyday": self.holyday,
            "status": self.status,
            "holyday_formated": self.holyday.strftime("%d/%m/%Y"),
        }

        return res


# Export alias
HolydayORM = Holydays
