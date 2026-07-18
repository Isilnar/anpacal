"""
SQLAlchemyUserRepository — implementación de UserRepository.

Principios:
- Un solo db.session.commit() por operación de escritura.
- delete() es soft-delete (status=0), nunca borra físicamente.
- save() encripta PII y calcula hashes antes de persistir.
- Todos los métodos de lectura retornan User (dominio), nunca UserORM.
- get_orm_by_id() es el único método que retorna UserORM —
  solo para que el adapter auth pueda llamar login_user(orm).
"""

from app import db
from app.domain.user.repositories import UserRepository
from app.domain.user.user import User
from app.infrastructure.crypto import encrypt_field, hash_field

from .mapper import orm_to_domain
from .orm import UserORM, UserStudentAssociation


class SQLAlchemyUserRepository(UserRepository):
    def find_by_id(self, user_id: int) -> User | None:
        orm = db.session.get(UserORM, user_id)
        return orm_to_domain(orm) if orm else None

    def find_by_username(self, username: str) -> User | None:
        orm = UserORM.query.filter_by(username=username).first()
        return orm_to_domain(orm) if orm else None

    def find_by_email_hash(self, email_hash: str) -> User | None:
        orm = UserORM.query.filter_by(email_hash=email_hash).first()
        return orm_to_domain(orm) if orm else None

    def find_by_number_id_hash(self, number_id_hash: str) -> User | None:
        orm = UserORM.query.filter_by(number_id_hash=number_id_hash).first()
        return orm_to_domain(orm) if orm else None

    def list_active(self) -> list[User]:
        orms = UserORM.query.filter_by(status=1).all()
        return [orm_to_domain(o) for o in orms]

    def save(self, user: User) -> User:
        """
        Insert o update:
        - Si user.id es None → nuevo registro.
        - Si user.id tiene valor → update del ORM existente.
        Encripta PII y calcula hashes antes del commit.
        """
        if user.id is None:
            orm = UserORM()
            db.session.add(orm)
        else:
            orm = db.session.get(UserORM, user.id)
            if orm is None:
                raise ValueError(f"User with id={user.id} not found")

        # Campos no-PII
        orm.username = user.username
        orm.name = user.name
        orm.surname = user.surname
        orm.address = user.address
        orm.status = user.status
        orm.user_partner = user.user_partner
        orm.ws_token = user.ws_token

        # Password — solo si el use case lo proporcionó (campo transitorio)
        if user.hashed_password is not None:
            orm.password = user.hashed_password

        # PII — encriptar + calcular hash para lookup
        if user.email:
            orm.email = encrypt_field(user.email)
            orm.email_hash = hash_field(user.email)
        if user.phone:
            orm.phone = encrypt_field(user.phone)
        if user.number_id:
            orm.number_id = encrypt_field(user.number_id)
            orm.number_id_hash = hash_field(user.number_id)

        db.session.commit()

        # Refrescar para obtener el id generado (caso insert)
        db.session.refresh(orm)
        return orm_to_domain(orm)

    def delete(self, user_id: int) -> None:
        """Soft-delete: status=0. No elimina físicamente el registro."""
        orm = db.session.get(UserORM, user_id)
        if orm is None:
            return
        orm.status = 0
        db.session.commit()

    # --- Método extra para el adapter auth (no forma parte del ABC de dominio) ---
    def get_orm_by_id(self, user_id: int) -> UserORM | None:
        """
        Retorna UserORM para que Flask-Login pueda llamar login_user(orm).
        Este método existe SOLO para el adapter auth_routes.py.
        El dominio no lo conoce.
        """
        return db.session.get(UserORM, user_id)

    def get_orm_by_username(self, username: str) -> UserORM | None:
        """
        Retorna UserORM para verificar password con check_password().
        Usado en AuthenticateUserUseCase.
        """
        return UserORM.query.filter_by(username=username).first()

    def get_partner_flag(self, student_id: int) -> bool:
        """
        Retorna True si TODOS los usuarios asociados al alumno son socios
        (user_partner == 'on').  Retorna False si alguno no es socio.
        Si el alumno no tiene usuarios asociados, retorna True (partner por defecto).
        """
        assocs = UserStudentAssociation.query.filter_by(student_id=student_id).all()
        if not assocs:
            return True
        for assoc in assocs:
            if assoc.user.user_partner is None or assoc.user.user_partner != "on":
                return False
        return True

    def get_student_ids_by_user(self, user_id: int) -> list[int]:
        """Retorna los student_ids asociados a un usuario via UserStudentAssociation."""
        assocs = UserStudentAssociation.query.filter_by(user_id=user_id).all()
        return [assoc.student_id for assoc in assocs]
