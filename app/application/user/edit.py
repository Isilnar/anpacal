"""
EditUserUseCase — edita un usuario existente.

Flujo:
1. Buscar user por id (UserNotFoundError si no existe).
2. Actualizar campos del User dominio con los datos del DTO.
3. Si new_password → re-hashear.
4. repo.save(user) — el repo re-encripta PII en cada save.
5. Retornar User actualizado.

El use case llama repo.save() exactamente una vez.
"""

from app.domain.user.services import CryptoService
from app.domain.user.user import User

from .dtos import UserEditDTO


class UserNotFoundError(Exception):
    pass


class EditUserUseCase:
    def __init__(self, repository, crypto: CryptoService, bcrypt=None):
        """
        repository: UserRepository.
        crypto: CryptoService.
        bcrypt: instancia de Flask-Bcrypt (opcional).
        """
        self.repository = repository
        self.crypto = crypto
        self.bcrypt = bcrypt

    def execute(self, dto: UserEditDTO) -> User:
        # 1. Obtener user existente
        user = self.repository.find_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User with id={dto.user_id} not found")

        # 2. Actualizar campos
        user.username = dto.username
        user.name = dto.name
        user.surname = dto.surname
        user.email = dto.email
        user.phone = dto.phone
        user.number_id = dto.number_id
        user.address = dto.address
        user.user_partner = dto.user_partner

        # 3. Re-hashear password si se proporcionó uno nuevo
        if dto.new_password:
            if self.bcrypt is not None:
                new_hashed = self.bcrypt.generate_password_hash(dto.new_password).decode("utf-8")
            else:
                new_hashed = dto.new_password
            self._set_password(user.id, new_hashed)

        # 4. Persistir (el repo re-encripta PII)
        updated_user = self.repository.save(user)

        # 5. Sync associations (roles, schools, students)
        self._sync_associations(dto)

        return updated_user

    def _sync_associations(self, dto: UserEditDTO) -> None:
        """Sync role, school, and student associations via ORM.

        Requires Flask app context (skipped silently in pure-unit-test
        environments where no app context is available).
        """
        from flask import has_app_context

        if not has_app_context():
            return

        from app import db
        from app.infrastructure.user.orm import (
            UserRoleAssociation,
            UserSchoolAssociation,
            UserStudentAssociation,
        )

        user_id = dto.user_id

        # Roles
        UserRoleAssociation.query.filter_by(user_id=user_id).delete()
        for role_id in dto.role_ids:
            db.session.add(UserRoleAssociation(user_id=user_id, role_id=role_id))

        # Schools
        UserSchoolAssociation.query.filter_by(user_id=user_id).delete()
        for school_id in dto.school_ids:
            db.session.add(UserSchoolAssociation(user_id=user_id, school_id=school_id))

        # Students
        UserStudentAssociation.query.filter_by(user_id=user_id).delete()
        for student_id in dto.student_ids:
            db.session.add(UserStudentAssociation(user_id=user_id, student_id=student_id))

        db.session.commit()

    def _set_password(self, user_id: int, hashed_pw: str) -> None:
        """Persiste el hash de password en el ORM directamente."""
        from app import db
        from app.infrastructure.user.orm import UserORM

        orm = db.session.get(UserORM, user_id)
        if orm is not None:
            orm.password = hashed_pw
            db.session.commit()
