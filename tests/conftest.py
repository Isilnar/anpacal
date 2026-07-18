import os
import threading
import time

import pytest

# CRÍTICO: setear antes de cualquier import de la app
os.environ.setdefault("TESTING", "1")

TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:?check_same_thread=False",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SECRET_KEY": "test-secret-key",
    "FERNET_KEY": "6TiOB1atiuV0uAS2EiR6x0iqxW4qO8d-sf2nZltF1L4=",
    "WTF_CSRF_ENABLED": False,
    "RATELIMIT_ENABLED": False,  # disable rate limiting in tests
    "LOGIN_DISABLED": False,
    "MAIL_SERVER": "localhost",
    "MAIL_PORT": 25,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": "",
    "MAIL_PASSWORD": "",
    "MAIL_RESPONSE_ADDRESS": "",
    "SERVER_NAME": None,
    # Defaults para _seed_defaults. Con threaded=False as requests son
    # secuenciais, así que non hai TOCTOU race.
    "DEFAULT_ROLES": [
        ("admin", "Administrador"),
        ("family", "Familia"),
        ("earlycare", "Coidadora madrugadores"),
        ("lunchcare", "Coidadora comedor"),
    ],
    "DEFAULT_COURSES": [
        (1, "4º EI"),
        (2, "5º EI"),
        (3, "6º EI"),
        (4, "1º EP"),
        (5, "2º EP"),
        (6, "3º EP"),
        (7, "4º EP"),
        (8, "5º EP"),
        (9, "6º EP"),
    ],
    "DEFAULT_DIET_INTOLERANCES": [
        ("1", "Sal", 1),
        ("2", "Azucre", 1),
        ("3", "Cacahuetes", 0),
        ("4", "Glute", 1),
        ("5", "Lácteos", 1),
        ("6", "Froitos Secos", 1),
        ("7", "Apio", 0),
        ("8", "Mostaza", 0),
        ("9", "Ovos", 1),
        ("10", "Sésamo", 0),
        ("11", "Peixe", 1),
        ("12", "Crustáceos", 1),
        ("13", "Moluscos", 1),
        ("14", "Soia", 1),
        ("15", "Sulfitos", 0),
        ("16", "Altramuces", 0),
    ],
}


@pytest.fixture(scope="session")
def app():
    """Flask app con SQLite in-memory — config inyectada ANTES de db.init_app."""
    from app import create_app
    from app import db as _db

    # test_config se pasa a create_app() y se aplica ANTES de db.init_app()
    # Así el engine SQLAlchemy usa :memory: desde el primer momento
    flask_app = create_app(test_config=TEST_CONFIG)

    # Verificación de seguridad: el engine debe apuntar a :memory:
    with flask_app.app_context():
        engine_url = str(_db.engine.url)
        assert ":memory:" in engine_url, (
            f"DANGER: engine apunta a DB real: {engine_url}. "
            "El engine NUNCA debe apuntar a la DB de producción en tests."
        )
        assert "check_same_thread=False" in engine_url, (
            f"check_same_thread=False es necesario para E2E (servidor en thread separado). Engine URL: {engine_url}"
        )
        _db.create_all()

        # Seed defaults igual que _seed_defaults() en main_routes.py,
        # pero sen depender de before_request (os tests non golpean main_bp).
        from app.infrastructure.intolerance.orm import DietIntoleranceORM
        from app.infrastructure.role.orm import RoleORM
        from app.infrastructure.school_course.orm import SchoolCourseORM

        for name, description in TEST_CONFIG.get("DEFAULT_ROLES", []):
            if not _db.session.query(RoleORM).filter_by(name=name).first():
                _db.session.add(RoleORM(name=name, description=description))

        for course_id, description in TEST_CONFIG.get("DEFAULT_COURSES", []):
            if not _db.session.get(SchoolCourseORM, course_id):
                _db.session.add(SchoolCourseORM(id=course_id, description=description))

        for intol_id, description, status in TEST_CONFIG.get("DEFAULT_DIET_INTOLERANCES", []):
            if not _db.session.get(DietIntoleranceORM, intol_id):
                _db.session.add(DietIntoleranceORM(id=intol_id, description=description, status=status))

        _db.session.commit()

    yield flask_app


@pytest.fixture(scope="session")
def db(app):
    """Retorna la instancia de db ya inicializada."""
    from app import db as _db

    with app.app_context():
        yield _db


@pytest.fixture(scope="function")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def live_server_url(app):
    """Levanta el servidor Flask en un thread para tests E2E.

    Nombre `live_server_url` (no `live_server`) para evitar colisión con
    pytest-flask, que intercepta cualquier fixture llamado `live_server`
    y espera un objeto con atributo `.app` (no un string).
    """
    # Use threaded=False so ALL requests run in the SAME server thread.
    # With threaded=True (Werkzeug default), each request gets a fresh thread
    # whose Flask-SQLAlchemy scoped session gets a new StaticPool connection
    # to the shared :memory: database — but the connection's session state
    # can cause Flask-Login's load_user to fail on subsequent requests.
    # Single-threaded: all requests share one server thread, one session.
    with app.app_context():
        thread = threading.Thread(target=lambda: app.run(port=5001, use_reloader=False, debug=False, threaded=False))
        thread.daemon = True
        thread.start()
        time.sleep(1)
        yield "http://localhost:5001"
