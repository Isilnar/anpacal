# auth_routes.py — Adapter: login/logout delegando a AuthenticateUserUseCase.

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import _
from flask_babel import lazy_gettext as _l
from flask_login import login_required, login_user, logout_user

from app import limiter
from app.application.user.authenticate import AuthenticateUserUseCase, AuthenticationError
from app.application.user.generate_token import GenerateTokenUseCase
from app.infrastructure.user.repository import SQLAlchemyUserRepository

auth = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


def _make_repo() -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository()


def _ensure_token(repo, domain_user) -> None:
    """Genera ws_token si el usuario aún no tiene uno."""
    if domain_user.ws_token is None:
        GenerateTokenUseCase(repo).execute(domain_user.id)


@auth.route("/login", methods=["GET", "POST"])
@limiter.limit(
    "10 per minute; 50 per hour",
    error_message=_l("Demasiados intentos de acceso. Agarde uns minutos."),
    methods=["POST"],
)
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    frm = request.form
    username = frm.get("username", "")
    repo = _make_repo()
    use_case = AuthenticateUserUseCase(repo)
    try:
        domain_user = use_case.execute(username, frm.get("password", ""))
    except AuthenticationError:
        logger.warning("Failed login attempt for username=%r ip=%s", username, request.remote_addr)
        flash(_("Nome ou contrasinal incorrectos"))
        return redirect(url_for("auth.login"))
    logger.info("Successful login username=%r ip=%s", username, request.remote_addr)
    _ensure_token(repo, domain_user)
    login_user(repo.get_orm_by_id(domain_user.id))
    return redirect(url_for("main_bp.index"))


@auth.route("/logout")
@login_required
def logout():
    from flask_login import current_user

    logger.info("Logout username=%r ip=%s", current_user.username, request.remote_addr)
    logout_user()
    return redirect(url_for("main_bp.index"))


@auth.route("/user-not-allowed")
@login_required
def user_not_allowed():
    return render_template("auth/not_allow_user.html")
