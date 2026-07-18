# init.py

import logging
import sys
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, redirect, request, session, url_for
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
babel = Babel()
mail_flask = Mail()
bcrypt = Bcrypt()
talisman = Talisman()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def _configure_logging(app: Flask) -> None:
    """Configure application logging.

    - DEBUG mode  → stdout only (human-friendly for development)
    - Production  → stdout + rotating file (logs/app.log, 5 MB × 3 backups)
    Format: timestamp | level | logger | message
    """
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    # Always log to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)

    # Rotating file in production
    handlers: list[logging.Handler] = [stdout_handler]
    if not app.config.get("DEBUG") and not app.config.get("TESTING"):
        import os

        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler("logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(fmt)
        handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers, force=True)

    # Quieten noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    app.logger.setLevel(level)
    app.logger.info("Logging configured — level=%s", logging.getLevelName(level))


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    if test_config:
        app.config.update(test_config)

    # ---------------------------------------------------------------------------
    # Startup guards — fail fast on insecure configuration
    # ---------------------------------------------------------------------------
    if not app.config.get("TESTING"):
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError(
                "SECRET_KEY is not set. Set the SECRET_KEY environment variable before starting the app."
            )
        if not app.config.get("FERNET_KEY"):
            raise RuntimeError(
                "FERNET_KEY is not set. Set the FERNET_KEY environment variable before starting the app."
            )

    _configure_logging(app)

    # ---------------------------------------------------------------------------
    # Security headers (Flask-Talisman)
    # Disabled in testing to avoid HTTPS redirects breaking the test client.
    # ---------------------------------------------------------------------------
    if not app.config.get("TESTING"):
        _csp = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "https://cdnjs.cloudflare.com",
                "https://cdn.jsdelivr.net",
                "https://code.jquery.com",
                # Allow inline scripts (Jinja2 templates use them — refactor later)
                "'unsafe-inline'",
            ],
            "style-src": [
                "'self'",
                "https://cdnjs.cloudflare.com",
                "https://cdn.jsdelivr.net",
                "'unsafe-inline'",
            ],
            "font-src": [
                "'self'",
                "https://cdnjs.cloudflare.com",
                "data:",
            ],
            "img-src": ["'self'", "data:"],
            "connect-src": ["'self'"],
            "frame-ancestors": ["'none'"],
        }
        talisman.init_app(
            app,
            force_https=False,  # handled by reverse proxy / certs in run.py
            strict_transport_security=False,  # enable when HTTPS is confirmed in prod
            content_security_policy=_csp,
            x_content_type_options=True,
            frame_options="DENY",
            referrer_policy="strict-origin-when-cross-origin",
            session_cookie_secure=False,  # set True when HTTPS confirmed in prod
            session_cookie_http_only=True,
            session_cookie_samesite="Lax",
        )

    db.init_app(app)
    mail_flask.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    # Allow CSRF token via X-CSRFToken header for fetch() JSON requests
    app.config["WTF_CSRF_CHECK_DEFAULT"] = True
    app.config.setdefault("WTF_CSRF_HEADERS", ["X-CSRFToken", "X-CSRF-Token"])

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .infrastructure.user.orm import UserORM

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        # session['next_url'] = request.path
        return redirect(url_for("auth.login"))

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(UserORM, int(user_id))

    def get_locale():
        lang = session.get("lang")
        if lang and lang in app.config.get("LANGUAGES", ["gl", "es", "en"]):
            return lang
        matched = request.accept_languages.best_match(app.config.get("LANGUAGES", ["gl", "es", "en"]))
        return matched or "gl"

    babel.init_app(app, locale_selector=get_locale)
    app.jinja_env.globals["get_locale"] = get_locale

    @app.context_processor
    def inject_menu_link():
        """Inyecta menu_link en todos los templates para la navbar."""
        try:
            from .application.menu.get_active_menu import GetActiveMenuUseCase
            from .infrastructure.menu.repository import SQLAlchemyMenuRepository

            menu = GetActiveMenuUseCase(SQLAlchemyMenuRepository()).execute()
            return {"menu_link": menu.menu_link if menu else "#"}
        except Exception:
            return {"menu_link": "#"}

    # blueprint for auth routes in our app
    from .adapters.views.auth_routes import auth as auth_bp

    app.register_blueprint(auth_bp)

    # blueprint for non-auth parts of app
    from .adapters.views.main_routes import main_bp

    app.register_blueprint(main_bp)

    # blueprint for calendar station routes (CA adapter — Ciclo C)
    from .adapters.views.calendar_station_routes import calendar_station as calendar_bp

    app.register_blueprint(calendar_bp)

    # blueprint for clean-architecture user adapters
    from .adapters.views.user_routes import user_bp

    app.register_blueprint(user_bp)

    from .adapters.views.student_routes import student_bp

    app.register_blueprint(student_bp)

    from .adapters.views.school_routes import school_bp

    app.register_blueprint(school_bp)

    from .adapters.views.menu_routes import menu_bp

    app.register_blueprint(menu_bp)

    from .adapters.views.holyday_routes import holyday_bp

    app.register_blueprint(holyday_bp)

    from .adapters.views.calendar_routes import calendar_bp as calendar_clean_bp

    app.register_blueprint(calendar_clean_bp)

    from .adapters.views.edit_registers_routes import edit_registers_bp

    app.register_blueprint(edit_registers_bp)

    from .adapters.views.reports_routes import earlycare_reports_bp, lunchcare_reports_bp, reports_bp

    app.register_blueprint(reports_bp)
    app.register_blueprint(earlycare_reports_bp)
    app.register_blueprint(lunchcare_reports_bp)

    with app.app_context():
        db.create_all()

    return app
