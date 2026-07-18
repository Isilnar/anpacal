# school_routes.py — Adapter: rutas CRUD de school delegando a use cases.
#
# Blueprint 'school_bp' con prefijo '/management/schools'.
# Convive con el blueprint 'management_station' en management.py (Strangler Fig).

from flask import Blueprint, flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_babel import _
from flask_login import login_required

from app.adapters.decorators import admin_required
from app.application.school.create import CreateSchoolUseCase, DuplicateSchoolError
from app.application.school.delete import DeleteSchoolUseCase
from app.application.school.dtos import SchoolCreateDTO, SchoolEditDTO
from app.application.school.edit import EditSchoolUseCase, SchoolNotFoundError
from app.application.school.get import GetSchoolUseCase
from app.application.school.list_schools import ListSchoolsUseCase
from app.infrastructure.school.repository import SQLAlchemySchoolRepository

school_bp = Blueprint("school_bp", __name__, url_prefix="/management/schools")


def _make_repo():
    return SQLAlchemySchoolRepository()


# ---------------------------------------------------------------------------
# GET / — listar schools activos
# ---------------------------------------------------------------------------
@school_bp.route("/")
@login_required
@admin_required
def list_schools():
    schools = ListSchoolsUseCase(_make_repo()).execute()
    return render_template(
        "station/management/edit_school.html",
        centers_list=schools,
        menu_link="",
    )


# ---------------------------------------------------------------------------
# POST / — crear school
# ---------------------------------------------------------------------------
@school_bp.route("/", methods=["POST"])
@login_required
@admin_required
def create_school():
    frm = request.form
    dto = SchoolCreateDTO(
        name=frm.get("centerName", ""),
        address=frm.get("centerAddress", ""),
        phone=frm.get("centerPhone", ""),
        email=frm.get("centerMail", ""),
    )
    try:
        CreateSchoolUseCase(_make_repo()).execute(dto)
        flash(_("Rexistrouse un novo centro"))
    except DuplicateSchoolError:
        flash(_("Xa existe un centro co nome e enderezo"))
    return redirect(url_for("school_bp.list_schools"))


# ---------------------------------------------------------------------------
# GET /<school_id> — obtener school (JSON)
# ---------------------------------------------------------------------------
@school_bp.route("/<int:school_id>")
@login_required
@admin_required
def get_school(school_id: int):
    try:
        school = GetSchoolUseCase(_make_repo()).execute(school_id)
        return make_response(jsonify(school.get_dict()), 200)
    except SchoolNotFoundError:
        return make_response(jsonify({"error": "not found"}), 404)


# ---------------------------------------------------------------------------
# POST /<school_id> — editar school
# ---------------------------------------------------------------------------
@school_bp.route("/<int:school_id>", methods=["POST"])
@login_required
@admin_required
def edit_school(school_id: int):
    frm = request.form
    dto = SchoolEditDTO(
        school_id=school_id,
        name=frm.get("centerName", ""),
        address=frm.get("centerAddress", ""),
        phone=frm.get("centerPhone", ""),
        email=frm.get("centerMail", ""),
    )
    try:
        EditSchoolUseCase(_make_repo()).execute(dto)
        flash(_("Modificáronse os parámetros do centro"))
    except SchoolNotFoundError:
        flash(_("Centro non atopado"))
    return redirect(url_for("school_bp.list_schools"))


# ---------------------------------------------------------------------------
# POST /<school_id>/delete — soft-delete school
# ---------------------------------------------------------------------------
@school_bp.route("/<int:school_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_school(school_id: int):
    try:
        DeleteSchoolUseCase(_make_repo()).execute(school_id)
        flash(_("Eliminouse o centro seleccionado"))
    except SchoolNotFoundError:
        flash(_("Centro non atopado"))
    return redirect(url_for("school_bp.list_schools"))
