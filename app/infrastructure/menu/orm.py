"""
MenuORM — ORM class defined directly here (infrastructure/menu).

Ciclo D2: Class body inlined from models/menu.py — app/models is no longer imported.
Class defined as Menu (original name), exported as MenuORM.
"""

from datetime import datetime

from app import db

__all__ = ["MenuORM"]


class Menu(db.Model):
    __table_name__ = "menu"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    menu_link = db.Column(db.String())
    status = db.Column(db.Integer(), default=1)


# Export alias
MenuORM = Menu
