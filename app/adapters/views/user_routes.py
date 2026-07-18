# user_routes.py — Adapter: rutas CRUD de usuario delegando a use cases.
#
# Blueprint 'user_bp' con prefijo '/management/users'.
# Convive con el blueprint 'management_station' en management.py (Strangler Fig).
# PR-4 hará el cleanup.

from flask import Blueprint, flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_babel import _
from flask_login import login_required

from app import bcrypt, db
from app.adapters.decorators import admin_required
from app.adapters.utils import get_current_schools, get_random_password, get_selected_roles
from app.application.user.create import CreateUserUseCase, DuplicateUsernameError
from app.application.user.delete import DeleteUserUseCase
from app.application.user.dtos import UserCreateDTO, UserEditDTO
from app.application.user.edit import EditUserUseCase, UserNotFoundError
from app.application.user.get import GetUserUseCase
from app.application.user.list_users import ListUsersUseCase
from app.infrastructure.user.crypto_service import FernetCryptoService
from app.infrastructure.user.mail_service import FlaskMailService
from app.infrastructure.user.orm import UserORM
from app.infrastructure.user.repository import SQLAlchemyUserRepository

user_bp = Blueprint("user_bp", __name__, url_prefix="/management/users")


def _make_repo():
    return SQLAlchemyUserRepository()


def _make_crypto():
    return FernetCryptoService()


def _make_mail():
    return FlaskMailService()


# ---------------------------------------------------------------------------
# GET / — listar usuarios activos
# ---------------------------------------------------------------------------
@user_bp.route("/")
@login_required
@admin_required
def list_users():
    repo = _make_repo()
    users = ListUsersUseCase(repo).execute()
    roles_list = get_selected_roles()
    schools_list = get_current_schools()
    return render_template(
        "station/management/edit_user.html",
        users_list=users,
        roles_list=roles_list,
        schools_list=schools_list,
        menu_link="",
    )


def _build_create_dto(frm) -> UserCreateDTO:
    """Construye UserCreateDTO desde los campos del formulario."""
    role_ids = [int(r) for r in frm.get("selectedRolesIds", "").split(",") if r]
    school_ids = [int(s) for s in frm.get("selectedSchoolsIds", "").split(",") if s]
    return UserCreateDTO(
        username=frm.get("userLogin", ""),
        name=frm.get("userName", ""),
        surname=frm.get("userSurname", ""),
        email=frm.get("userMail", ""),
        phone=frm.get("userPhone", ""),
        number_id=frm.get("numberID", ""),
        address=frm.get("userAddress", ""),
        password=frm.get("userPass", ""),
        user_partner=frm.get("userPartner", ""),
        role_ids=role_ids,
        school_ids=school_ids,
    )


# ---------------------------------------------------------------------------
# POST / — crear usuario
# ---------------------------------------------------------------------------
@user_bp.route("/", methods=["POST"])
@login_required
@admin_required
def create_user():
    dto = _build_create_dto(request.form)
    repo = _make_repo()
    use_case = CreateUserUseCase(repo, _make_crypto(), _make_mail(), bcrypt)
    try:
        use_case.execute(dto)
        flash(_("Rexistrouse un novo usuario"))
    except DuplicateUsernameError:
        flash(_("Xa existe un usuario co mesmo nome de usuario"))
    return redirect(url_for("user_bp.list_users"))


# ---------------------------------------------------------------------------
# GET /<user_id> — obtener usuario (JSON)
# ---------------------------------------------------------------------------
@user_bp.route("/<int:user_id>")
@login_required
@admin_required
def get_user(user_id: int):
    repo = _make_repo()
    try:
        user = GetUserUseCase(repo).execute(user_id)
    except UserNotFoundError:
        return make_response(jsonify({"error": "not found"}), 404)

    # Construir el dict con el formato exacto que espera el template JS
    # (equivalente al legacy load_user_post + User.get_dict())
    orm = db.session.get(UserORM, user_id)

    # Roles con is_selected marcado para este usuario
    roles = get_selected_roles(orm)

    # Escuelas con is_selected marcado para este usuario
    schools = get_current_schools(orm)

    # Alumnos vinculados — string de nombres + lista de IDs
    from app.infrastructure.student.orm import StudentORM
    from app.infrastructure.user.orm import UserStudentAssociation

    students_string = ""
    students_ids = []
    for assoc in UserStudentAssociation.query.filter_by(user_id=user_id).all():
        student = db.session.get(StudentORM, assoc.student_id)
        if student:
            students_ids.append(student.id)
            if students_string:
                students_string += "; "
            students_string += f"{student.surname}, {student.name}"

    data = {
        "name": user.name,
        "surname": user.surname,
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "address": user.address,
        "number_id": user.number_id,
        "status": user.status,
        "user_partner": user.user_partner,
        "roles": roles,
        "schools": schools,
        "students_associated": students_string,
        "students_associated_ids": students_ids,
    }
    return make_response(jsonify(data), 200)


# ---------------------------------------------------------------------------
# POST /<user_id> — editar usuario
# ---------------------------------------------------------------------------
@user_bp.route("/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def edit_user(user_id: int):
    frm = request.form
    role_ids = [int(r) for r in frm.get("selectedRolesIds", "").split(",") if r]
    school_ids = [int(s) for s in frm.get("selectedSchoolsIds", "").split(",") if s]
    student_ids = [int(s) for s in frm.get("selectedStudentsIds", "").split(",") if s]

    dto = UserEditDTO(
        user_id=user_id,
        username=frm.get("userLogin", ""),
        name=frm.get("userName", ""),
        surname=frm.get("userSurname", ""),
        email=frm.get("userMail", ""),
        phone=frm.get("userPhone", ""),
        number_id=frm.get("numberID", ""),
        address=frm.get("userAddress", ""),
        user_partner=frm.get("userPartner", ""),
        new_password=frm.get("userPass") or None,
        role_ids=role_ids,
        school_ids=school_ids,
        student_ids=student_ids,
    )

    repo = _make_repo()
    use_case = EditUserUseCase(repo, _make_crypto(), bcrypt)
    try:
        use_case.execute(dto)
        flash(_("Modificáronse os parámetros do usuario"))
    except UserNotFoundError:
        flash(_("Usuario non atopado"))

    # Resend password by email if requested
    if frm.get("sendPassUserId"):
        password = frm.get("userPass", "")
        email = frm.get("userMail", "")
        username = frm.get("userLogin", "")
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Resend credentials requested: user=%s, email=%s, has_password=%s", username, email, bool(password))
        if email and password:
            try:
                mail_service = _make_mail()
                mail_service.send_credentials(email=email, username=username, password=password)
                flash(_("Enviáronse as credenciais por correo electrónico"))
                logger.info("Credentials email sent successfully to %s", email)
            except Exception as e:
                logger.error("Failed to send credentials email: %s", e)
                flash(_("Erro ao enviar o correo: %(error)s", error=str(e)))
        elif not email:
            flash(_("Non se pode enviar: o usuario non ten correo electrónico"))
        elif not password:
            flash(_("Non se pode enviar: debe introducir unha contrasinal no campo"))

    return redirect(url_for("user_bp.list_users"))


# ---------------------------------------------------------------------------
# POST /<user_id>/delete — soft-delete usuario
# ---------------------------------------------------------------------------
@user_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id: int):
    repo = _make_repo()
    use_case = DeleteUserUseCase(repo)
    try:
        use_case.execute(user_id)
        flash(_("Eliminouse o usuario seleccionado"))
    except UserNotFoundError:
        flash(_("Usuario non atopado"))

    return redirect(url_for("user_bp.list_users"))


# ---------------------------------------------------------------------------
# POST /generate-password — contraseña aleatoria (JSON)
# ---------------------------------------------------------------------------
@user_bp.route("/generate-password", methods=["POST"])
@login_required
@admin_required
def generate_password():
    return make_response(jsonify({"password": get_random_password()}), 200)


# ---------------------------------------------------------------------------
# POST /check-username — comproba se existe un nome de usuario (JSON)
# Migrado verbatim de management.py → check_exists_username
# ---------------------------------------------------------------------------
@user_bp.route("/check-username", methods=["POST"])
@login_required
def check_exists_username():
    result = {"success": True}

    user_login = request.json.get("username")

    tmp = UserORM.query.filter_by(username=user_login).first()
    if tmp is None:
        result["exists"] = 0
    else:
        result["exists"] = 1

    res = make_response(jsonify(result), 200)

    return res


# ---------------------------------------------------------------------------
# POST /change-password — cambia o contrasinal do usuario (JSON)
# Cualquier usuario autenticado puede cambiar su propia contraseña.
# Un admin puede cambiar la de cualquier usuario.
# ---------------------------------------------------------------------------
@user_bp.route("/change-password", methods=["POST"])
@login_required
def password_change_user():
    from flask_login import current_user

    result = {"success": True}

    frm = request.json
    user_id = int(frm.get("userId"))
    old_password = frm.get("passwordOld")
    new_password = frm.get("passwordNew")

    # Solo el propio usuario o un admin puede cambiar la contraseña
    if user_id != current_user.id and not current_user.is_admin():
        return make_response(jsonify({"error": _("Non autorizado")}), 403)

    tmp_user = UserORM.query.filter_by(id=user_id).first()
    if tmp_user is None:
        return make_response(jsonify({"error": _("Usuario non atopado")}), 404)

    old_match = bcrypt.check_password_hash(tmp_user.password, old_password)

    if old_match:
        tmp_user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()
    else:
        result["success"] = False

    res = make_response(jsonify(result), 200)

    return res
