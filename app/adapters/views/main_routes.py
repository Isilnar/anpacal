# main_routes.py — Adapter: rutas principales (/, /offline, /favicon.ico).
#
# Blueprint 'main_bp'.
# before_request seeder: reads via repos, bootstrap writes via annotated db.session.

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from app import db
from app.infrastructure.intolerance.orm import DietIntoleranceORM
from app.infrastructure.intolerance.repository import SQLAlchemyDietIntoleranceRepository
from app.infrastructure.role.orm import RoleORM
from app.infrastructure.role.repository import SQLAlchemyRoleRepository
from app.infrastructure.school_course.orm import SchoolCourseORM
from app.infrastructure.school_course.repository import SQLAlchemySchoolCourseRepository

main_bp = Blueprint("main_bp", __name__)


@main_bp.before_request
def _seed_defaults():
    """Seeds Role, SchoolCourses, DietIntolerance from config on every request.

    Reads: repos (CA-compliant).
    Writes: db.session.add (BOOTSTRAP-ORM: acceptable — one-time table initialisation).
    """
    role_repo = SQLAlchemyRoleRepository()
    existing_role_names = {r.name for r in role_repo.list_all()}
    for name, description in current_app.config.get("DEFAULT_ROLES", []):
        if name not in existing_role_names:
            db.session.add(RoleORM(name=name, description=description))  # BOOTSTRAP-ORM
            db.session.commit()

    course_repo = SQLAlchemySchoolCourseRepository()
    for course_id, description in current_app.config.get("DEFAULT_COURSES", []):
        if course_repo.get_by_id(course_id) is None:
            db.session.add(SchoolCourseORM(id=course_id, description=description))  # BOOTSTRAP-ORM
            db.session.commit()

    intolerance_repo = SQLAlchemyDietIntoleranceRepository()
    for intol_id, description, status in current_app.config.get("DEFAULT_DIET_INTOLERANCES", []):
        if intolerance_repo.get_by_id(intol_id) is None:
            db.session.add(DietIntoleranceORM(id=intol_id, description=description, status=status))  # BOOTSTRAP-ORM
            db.session.commit()


@main_bp.route("/")
def index():
    return render_template("main/index.html")


@main_bp.route("/offline")
def offline():
    return render_template("main/offline.html")


@main_bp.route("/service-worker.js")
def service_worker():
    """Serve SW from root so its scope covers the entire app."""
    return send_from_directory("static/js", "service-worker.js", mimetype="application/javascript")


@main_bp.route("/favicon.ico")
def favicon():
    return send_from_directory("static/images", "favicon.ico", mimetype="image/vnd.microsoft.icon")


@main_bp.route("/set-language/<lang>", methods=["POST"])
def set_language(lang):
    allowed = current_app.config.get("LANGUAGES", ["gl", "es", "en"])
    if lang in allowed:
        session["lang"] = lang
    return redirect(request.referrer or url_for("main_bp.index"))


@main_bp.route("/manifest.json")
def manifest():
    """Serve PWA manifest dynamically from app config."""
    app_title = current_app.config.get("APP_TITLE", "ANPA")
    app_desc = current_app.config.get("APP_DESC", "")
    data = {
        "short_name": app_title,
        "name": app_title,
        "description": app_desc,
        "theme_color": "#34A5DA",
        "background_color": "#FFFFFF",
        "icons": [
            {"src": "/static/images/android-launchericon-48-48.png", "type": "image/png", "sizes": "48x48"},
            {"src": "/static/images/android-launchericon-96-96.png", "type": "image/png", "sizes": "96x96"},
            {"src": "/static/images/android-launchericon-144-144.png", "type": "image/png", "sizes": "144x144"},
            {"src": "/static/images/android-launchericon-192-192.png", "type": "image/png", "sizes": "192x192"},
            {"src": "/static/images/android-launchericon-512-512.png", "type": "image/png", "sizes": "512x512"},
        ],
        "start_url": "/?source=pwa",
        "display": "standalone",
        "orientation": "portrait",
    }
    response = jsonify(data)
    response.headers["Content-Type"] = "application/manifest+json"
    return response
