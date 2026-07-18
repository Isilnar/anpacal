"""
RoleORM — ORM class defined directly here (infrastructure/role).

Ciclo D2: Class body inlined from models/user.py — app/models is no longer imported.
Class defined as Role (for SQLAlchemy string-relationship resolution),
exported as RoleORM for infrastructure naming convention.
"""

from app import db

__all__ = ["RoleORM"]


class Role(db.Model):
    # Our Role has three fields, ID, name and description
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship("UserRoleAssociation", back_populates="role")

    # __str__ is required by Flask-Admin, so we can have human-readable
    #  values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception
    # TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


# Export alias
RoleORM = Role
