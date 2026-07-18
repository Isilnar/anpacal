# holyday_routes.py — Adapter: rutas CRUD de holyday delegando a use cases.
#
# Blueprint 'holyday_bp' con prefijo '/management/holydays'.
# Convive con el blueprint 'management_station' en management.py (Strangler Fig).

from datetime import datetime

from flask import Blueprint, flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_babel import _
from flask_login import login_required

from app.adapters.decorators import admin_required
from app.application.holyday.create import CreateHolydayUseCase, DuplicateHolydayError
from app.application.holyday.delete import DeleteHolydayUseCase
from app.application.holyday.dtos import HolydayCreateDTO, HolydayEditDTO
from app.application.holyday.edit import EditHolydayUseCase
from app.application.holyday.get import GetHolydayUseCase, HolydayNotFoundError
from app.application.holyday.list_holydays import ListHolydaysUseCase
from app.infrastructure.holyday.repository import SQLAlchemyHolydayRepository

holyday_bp = Blueprint("holyday_bp", __name__, url_prefix="/management/holydays")


def _make_repo():
    return SQLAlchemyHolydayRepository()


# ---------------------------------------------------------------------------
# GET / — listar holydays activos
# ---------------------------------------------------------------------------
@holyday_bp.route("/")
@login_required
@admin_required
def list_holydays():
    holydays = ListHolydaysUseCase(_make_repo()).execute()
    return render_template(
        "station/management/edit_holydays.html",
        holydays_list=holydays,
        menu_link="",
    )


# ---------------------------------------------------------------------------
# POST / — crear holyday
# ---------------------------------------------------------------------------
@holyday_bp.route("/", methods=["POST"])
@login_required
@admin_required
def create_holyday():
    frm = request.form
    raw_date = frm.get("dataHolydayDateValue", "")
    holyday_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
    dto = HolydayCreateDTO(holyday=holyday_date)
    try:
        CreateHolydayUseCase(_make_repo()).execute(dto)
        flash(_("Rexistrouse un novo día festivo"))
    except DuplicateHolydayError:
        flash(_("Xa existe un día festivo con esa data"))
    return redirect(url_for("holyday_bp.list_holydays"))


# ---------------------------------------------------------------------------
# GET /<holyday_id> — obtener holyday (JSON)
# ---------------------------------------------------------------------------
@holyday_bp.route("/<int:holyday_id>")
@login_required
@admin_required
def get_holyday(holyday_id: int):
    try:
        holyday = GetHolydayUseCase(_make_repo()).execute(holyday_id)
        return make_response(jsonify(holyday.get_dict()), 200)
    except HolydayNotFoundError:
        return make_response(jsonify({"error": "not found"}), 404)


# ---------------------------------------------------------------------------
# POST /<holyday_id> — editar holyday
# ---------------------------------------------------------------------------
@holyday_bp.route("/<int:holyday_id>", methods=["POST"])
@login_required
@admin_required
def edit_holyday(holyday_id: int):
    frm = request.form
    raw_date = frm.get("dataHolydayDateValue", "")
    holyday_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
    dto = HolydayEditDTO(holyday_id=holyday_id, holyday=holyday_date)
    try:
        EditHolydayUseCase(_make_repo()).execute(dto)
        flash(_("Modificouse o día festivo"))
    except Exception:
        flash(_("Día festivo non atopado"))
    return redirect(url_for("holyday_bp.list_holydays"))


# ---------------------------------------------------------------------------
# POST /<holyday_id>/delete — soft-delete holyday
# ---------------------------------------------------------------------------
@holyday_bp.route("/<int:holyday_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_holyday(holyday_id: int):
    try:
        DeleteHolydayUseCase(_make_repo()).execute(holyday_id)
        flash(_("Eliminouse o día festivo seleccionado"))
    except Exception:
        flash(_("Día festivo non atopado"))
    return redirect(url_for("holyday_bp.list_holydays"))
