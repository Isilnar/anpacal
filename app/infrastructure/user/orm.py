"""
User ORM classes defined directly here (infrastructure/user).

Ciclo D2: Class bodies inlined from models/user.py — app/models is no longer imported.
RoleORM re-exported from infrastructure/role/orm.py.
Classes defined with original names for SQLAlchemy string-relationship resolution.
"""

from datetime import datetime
from hashlib import sha512

from flask_login import UserMixin

from app import bcrypt, db
from app.infrastructure.role.orm import RoleORM  # noqa: F401 — re-export

__all__ = ["UserORM", "RoleORM", "UserRoleAssociation", "UserStudentAssociation", "UserSchoolAssociation"]


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128))
    last_update = db.Column(db.DateTime(), default=datetime.now)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    phone = db.Column(db.String(120))
    email = db.Column(db.String(250))
    address = db.Column(db.String(300))
    number_id = db.Column(db.String(120))
    number_id_hash = db.Column(db.String(64))
    email_hash = db.Column(db.String(64))
    user_partner = db.Column(db.String())
    ws_token = db.Column(db.Text, unique=True)
    status = db.Column(db.Integer(), default=1)

    roles = db.relationship("UserRoleAssociation", back_populates="user")

    students = db.relationship("UserStudentAssociation", back_populates="user")

    schools = db.relationship("UserSchoolAssociation", back_populates="user")

    def check_password(self, password):
        if self.status == 0:
            return 0
        return bcrypt.check_password_hash(self.password, password)

    def __has_role__(self, role_name):
        if role_name is not None:
            q = User.query.join(UserRoleAssociation).join(RoleORM)
            q = q.filter(User.id == self.id)
            q = q.filter(RoleORM.name == role_name)
            if len(q.all()) == 1:
                return 1
        return 0

    def is_admin(self):
        return self.__has_role__("admin")

    def is_family(self):
        return self.__has_role__("family")

    def is_lunchcare(self):
        return self.__has_role__("lunchcare")

    def is_earlycare(self):
        return self.__has_role__("earlycare")

    def update_token(self):
        if self.last_update is None:
            self.last_update = datetime.now()
        st = self.last_update.strftime("%Y%m%d%H%M%S%f")
        st = f"{st}-{self.username}"
        self.ws_token = sha512(st.encode("utf-8")).hexdigest()

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
            if len(fullname) > 0 and self.surname != " ":
                fullname = f"{self.surname}, {fullname}"
            else:
                fullname = f"{self.name}"

        return fullname


# Export alias
UserORM = User


class UserRoleAssociation(db.Model):
    __tablename__ = "user_role_association"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), primary_key=True)
    role = db.relationship("Role", back_populates="users")
    user = db.relationship("User", back_populates="roles")


class UserStudentAssociation(db.Model):
    __tablename__ = "user_student_association"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), primary_key=True)
    student = db.relationship("Student", back_populates="users")
    user = db.relationship("User", back_populates="students")


class UserSchoolAssociation(db.Model):
    __tablename__ = "user_school_association"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), primary_key=True)
    school = db.relationship("School", back_populates="users")
    user = db.relationship("User", back_populates="schools")
