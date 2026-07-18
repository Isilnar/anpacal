"""
CreateUserUseCase — crea un nuevo usuario.

Flujo:
1. Verificar que el username no exista (DuplicateUsernameError si existe).
2. Hashear password con bcrypt (o sin bcrypt según config).
3. Construir User dominio con los datos del DTO + hashed_password.
4. repo.save(user) — el repo encripta PII, calcula hashes y persiste la
   password hasheada en un ÚNICO commit.
5. mail_service.send_credentials() — enviar credenciales por email.
6. Retornar User creado.

El use case llama repo.save() exactamente una vez (sin commits extra).
"""

from app.domain.user.services import CryptoService, MailService
from app.domain.user.user import User

from .dtos import UserCreateDTO


class DuplicateUsernameError(Exception):
    pass


class CreateUserUseCase:
    def __init__(self, repository, crypto: CryptoService, mail_service: MailService, bcrypt=None):
        """
        repository: UserRepository (o compatible con SQLAlchemyUserRepository).
        crypto: CryptoService — para encriptar/hashear PII.
        mail_service: MailService — para enviar credenciales.
        bcrypt: instancia de Flask-Bcrypt (opcional; si es None, password se guarda en claro).
        """
        self.repository = repository
        self.crypto = crypto
        self.mail_service = mail_service
        self.bcrypt = bcrypt

    def execute(self, dto: UserCreateDTO) -> User:
        # 1. Verificar unicidad de username
        existing = self.repository.find_by_username(dto.username)
        if existing is not None:
            raise DuplicateUsernameError(f"Username '{dto.username}' already exists")

        # 2. Hashear password
        if self.bcrypt is not None:
            hashed_pw = self.bcrypt.generate_password_hash(dto.password).decode("utf-8")
        else:
            hashed_pw = dto.password

        # 3. Construir User dominio (sin id — save lo asignará)
        user = User(
            username=dto.username,
            name=dto.name,
            surname=dto.surname,
            email=dto.email,
            phone=dto.phone,
            number_id=dto.number_id,
            address=dto.address,
            user_partner=dto.user_partner,
            status=1,
            hashed_password=hashed_pw,
        )

        # 4. Persistir — el repo encripta PII y setea password en UN solo commit
        saved_user = self.repository.save(user)

        # 4b. Sync role and school associations
        self._sync_associations(saved_user.id, dto)

        # 5. Enviar credenciales
        if dto.email:
            self.mail_service.send_credentials(
                email=dto.email,
                username=dto.username,
                password=dto.password,  # password en claro para el email
            )

        return saved_user

    def _sync_associations(self, user_id: int, dto: UserCreateDTO) -> None:
        """Persist role and school associations for the newly created user."""
        from flask import has_app_context

        if not has_app_context():
            return

        from app import db
        from app.infrastructure.user.orm import UserRoleAssociation, UserSchoolAssociation

        for role_id in dto.role_ids:
            db.session.add(UserRoleAssociation(user_id=user_id, role_id=role_id))

        for school_id in dto.school_ids:
            db.session.add(UserSchoolAssociation(user_id=user_id, school_id=school_id))

        db.session.commit()
