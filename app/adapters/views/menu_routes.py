# menu_routes.py — Adapter: rutas de menú delegando a use cases.
#
# Blueprint 'menu_bp' con prefijo '/management/menu'.
# Convive con management_menu y management_menu_post en management.py (Strangler Fig).

from flask import Blueprint, flash, render_template, request
from flask_babel import _
from flask_login import login_required

from app.adapters.decorators import admin_required
from app.application.menu.get_active_menu import GetActiveMenuUseCase
from app.application.menu.set_menu import SetMenuUseCase
from app.infrastructure.menu.repository import SQLAlchemyMenuRepository

menu_bp = Blueprint("menu_bp", __name__, url_prefix="/management/menu")


def _make_repo():
    return SQLAlchemyMenuRepository()


# ---------------------------------------------------------------------------
# GET / — mostrar menú activo
# ---------------------------------------------------------------------------
@menu_bp.route("/")
@login_required
@admin_required
def get_menu():
    menu = GetActiveMenuUseCase(_make_repo()).execute()
    menu_link = menu.menu_link if menu else ""
    return render_template("station/management/edit_menu.html", menu_link=menu_link)


# ---------------------------------------------------------------------------
# POST / — establecer nuevo menú activo
# ---------------------------------------------------------------------------
@menu_bp.route("/", methods=["POST"])
@login_required
@admin_required
def set_menu():
    menu_link = request.form.get("menu_link", "")
    menu = SetMenuUseCase(_make_repo()).execute(menu_link)
    flash(_("Menú actualizado"))
    return render_template("main/index.html", menu_link=menu.menu_link)
