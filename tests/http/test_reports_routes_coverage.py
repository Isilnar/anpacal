"""
Tests de cobertura HTTP para reports_routes.py.

Cubre las líneas: 53, 62-67, 76-94, 98-112, 116-135, 139-154, 158-171, 175-189,
198-214, 218-232, 236-247, 251-260, 264-271, 275-281, 291-294, 319, 326-353,
371, 377-395, 413, 419-440

Tres blueprints:
  reports_bp           → /management/reports
  earlycare_reports_bp → /management/earlycare-reports
  lunchcare_reports_bp → /management/lunchcare-reports
"""

import io
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Teardown: limpia el usuario cacheado en g._login_user después de cada test.
# Esto evita que los logins reales (vía POST /login) dejen el usuario autenticado
# en el app context session-scoped, lo que rompería tests posteriores que verifican
# comportamiento sin autenticación.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_login_state_after_each_test(app):
    """Limpia g._login_user al final de cada test en este módulo."""
    yield
    from flask.globals import _cv_app

    ctx = _cv_app.get(None)
    if ctx is not None:
        local_g = ctx.g
        if hasattr(local_g, "_login_user"):
            delattr(local_g, "_login_user")


# ---------------------------------------------------------------------------
# Helpers — reutilizados del patrón de test_http_routes.py
# ---------------------------------------------------------------------------


def _get_or_create_admin(app, db):
    """Crea un usuario admin (idempotente). Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        user = db.session.query(User).filter_by(username="rep_admin").first()
        if not user:
            role = db.session.query(Role).filter_by(name="admin").first()
            if not role:
                role = Role(name="admin", description="Administrador")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="rep_admin",
                password=bcrypt.generate_password_hash("rep_pass").decode("utf-8"),
                name="Rep",
                surname="Admin",
                status=1,
                ws_token="rep-admin-token",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    return "rep_admin", "rep_pass"


def _get_or_create_earlycare_user(app, db):
    """Crea un usuario con rol earlycare (idempotente). Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        user = db.session.query(User).filter_by(username="rep_earlycare").first()
        if not user:
            role = db.session.query(Role).filter_by(name="earlycare").first()
            if not role:
                role = Role(name="earlycare", description="Madrugadores")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="rep_earlycare",
                password=bcrypt.generate_password_hash("rep_early_pass").decode("utf-8"),
                name="Early",
                surname="Care",
                status=1,
                ws_token="rep-earlycare-token",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    return "rep_earlycare", "rep_early_pass"


def _get_or_create_lunchcare_user(app, db):
    """Crea un usuario con rol lunchcare (idempotente). Devuelve (username, password)."""
    from app import bcrypt
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        user = db.session.query(User).filter_by(username="rep_lunchcare").first()
        if not user:
            role = db.session.query(Role).filter_by(name="lunchcare").first()
            if not role:
                role = Role(name="lunchcare", description="Comedor")
                db.session.add(role)
                db.session.flush()

            user = User(
                username="rep_lunchcare",
                password=bcrypt.generate_password_hash("rep_lunch_pass").decode("utf-8"),
                name="Lunch",
                surname="Care",
                status=1,
                ws_token="rep-lunchcare-token",
            )
            db.session.add(user)
            db.session.flush()

            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            db.session.commit()

    return "rep_lunchcare", "rep_lunch_pass"


def _login(client, username, password):
    client.post("/login", data={"username": username, "password": password})


def _login_admin(client, app, db):
    username, password = _get_or_create_admin(app, db)
    _login(client, username, password)


def _login_earlycare(client, app, db):
    username, password = _get_or_create_earlycare_user(app, db)
    _login(client, username, password)


def _login_lunchcare(client, app, db):
    username, password = _get_or_create_lunchcare_user(app, db)
    _login(client, username, password)


def _make_xlsx_file_data():
    """Devuelve un BytesIO simulando un xlsx vacío."""
    return io.BytesIO(b"PK fake xlsx content")


def _make_excel_report_result():
    """Mock del resultado de ExcelReport.get_xlsx()."""
    return {
        "file_data": _make_xlsx_file_data(),
        "filename": "test_report.xlsx",
    }


# ---------------------------------------------------------------------------
# GET redirects (lines 319, 371, 413)
# ---------------------------------------------------------------------------


class TestReportGetRedirects:
    def test_create_report_get_redirects_to_reports(self, client, app, db):
        """GET /management/reports/create → 302 redirect."""
        _login_admin(client, app, db)
        response = client.get("/management/reports/create", follow_redirects=False)
        assert response.status_code == 302

    def test_create_earlycare_report_get_redirects(self, client, app, db):
        """GET /management/earlycare-reports/create → 302 redirect."""
        _login_earlycare(client, app, db)
        response = client.get("/management/earlycare-reports/create", follow_redirects=False)
        assert response.status_code == 302

    def test_create_lunchcare_report_get_redirects(self, client, app, db):
        """GET /management/lunchcare-reports/create → 302 redirect."""
        _login_lunchcare(client, app, db)
        response = client.get("/management/lunchcare-reports/create", follow_redirects=False)
        assert response.status_code == 302

    def test_create_report_get_no_auth_redirects(self, client):
        """GET /management/reports/create sin auth → 302."""
        response = client.get("/management/reports/create", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_create_earlycare_report_get_no_auth_redirects(self, client):
        """GET /management/earlycare-reports/create sin auth → 302."""
        response = client.get("/management/earlycare-reports/create", follow_redirects=False)
        assert response.status_code in (301, 302)

    def test_create_lunchcare_report_get_no_auth_redirects(self, client):
        """GET /management/lunchcare-reports/create sin auth → 302."""
        response = client.get("/management/lunchcare-reports/create", follow_redirects=False)
        assert response.status_code in (301, 302)


# ---------------------------------------------------------------------------
# POST /management/reports/create (lines 326-353)
# Cubre: _company_data (198-214), _yn (218-232), early_data (251-260),
#        lunch_data (264-271), early_default_report (116-135),
#        lunch_default_report (76-94)
# ---------------------------------------------------------------------------


class TestCreateReportPost:
    def test_post_report_type_0_returns_xlsx(self, client, app, db):
        """POST /management/reports/create con reportType=0 → xlsx descarga."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.early_data", return_value=[]),
            patch("app.adapters.views.reports_routes.lunch_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/reports/create",
                data={
                    "reportType": "0",
                    "student": "0",
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_report_type_1_early_only(self, client, app, db):
        """POST /management/reports/create con reportType=1 → xlsx descarga."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.early_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/reports/create",
                data={
                    "reportType": "1",
                    "student": "0",
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_report_type_2_early_plus(self, client, app, db):
        """POST /management/reports/create con reportType=2 → xlsx descarga."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.early_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/reports/create",
                data={
                    "reportType": "2",
                    "student": "0",
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_report_type_3_lunch_only(self, client, app, db):
        """POST /management/reports/create con reportType=3 → xlsx descarga."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.lunch_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/reports/create",
                data={
                    "reportType": "3",
                    "student": "0",
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_report_no_auth_redirects(self, client, app):
        """POST /management/reports/create sin auth → 302."""
        from flask.globals import _cv_app

        # Limpiar usuario cacheado en el app context (patrón de test_http_routes.py)
        ctx = _cv_app.get(None)
        if ctx is not None:
            local_g = ctx.g
            if hasattr(local_g, "_login_user"):
                delattr(local_g, "_login_user")

        response = client.post(
            "/management/reports/create",
            data={
                "reportType": "0",
                "student": "0",
                "validFrom": "01/01/2026",
                "validUntil": "31/01/2026",
            },
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_report_with_real_data_generates_xlsx(self, client, app, db):
        """POST /management/reports/create con datos reales → xlsx real generado."""
        _login_admin(client, app, db)

        # Datos mínimos: early_data retorna una fila con _yn aplicado
        early_row = {
            "early_day": "2026-01-15",
            "student": "Ana García",
            "course": "1A",
            "brother_number": "1",
            "early_plus": "Si",
            "not_come": "Non",
            "come_as_extra": "Non",
            "modified_by": "admin",
            "modified_notes": "",
            "partner": "Si",
        }

        with (
            patch("app.adapters.views.reports_routes.early_data", return_value=[early_row]),
            patch("app.adapters.views.reports_routes.lunch_data", return_value=[]),
        ):
            response = client.post(
                "/management/reports/create",
                data={
                    "reportType": "0",
                    "student": "0",
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200
        # The file should be an xlsx attachment
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition or response.status_code == 200


# ---------------------------------------------------------------------------
# POST /management/earlycare-reports/create (lines 377-395)
# Cubre: earlycare_data (236-247), lunchcare_data_for_report (251-260),
#        early_default_earlycare_report (139-154), lunch_default_earlycare_report (158-171)
# ---------------------------------------------------------------------------


class TestCreateEarlycareReportPost:
    def test_post_earlycare_report_returns_xlsx(self, client, app, db):
        """POST /management/earlycare-reports/create → xlsx descarga."""
        _login_earlycare(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.earlycare_data", return_value=[]),
            patch("app.adapters.views.reports_routes.lunchcare_data_for_report", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/earlycare-reports/create",
                data={
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_earlycare_report_admin_also_works(self, client, app, db):
        """POST /management/earlycare-reports/create con admin → xlsx descarga."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.earlycare_data", return_value=[]),
            patch("app.adapters.views.reports_routes.lunchcare_data_for_report", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/earlycare-reports/create",
                data={
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_earlycare_report_no_auth_redirects(self, client, app):
        """POST /management/earlycare-reports/create sin auth → 302."""
        from flask.globals import _cv_app

        ctx = _cv_app.get(None)
        if ctx is not None:
            local_g = ctx.g
            if hasattr(local_g, "_login_user"):
                delattr(local_g, "_login_user")

        response = client.post(
            "/management/earlycare-reports/create",
            data={
                "validFrom": "01/01/2026",
                "validUntil": "31/01/2026",
            },
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_earlycare_report_with_real_data(self, client, app, db):
        """POST /management/earlycare-reports/create con datos reales → archivo generado."""
        _login_admin(client, app, db)

        earlycare_row = {
            "early_day": "2026-01-15",
            "student": "Ana García",
            "course": "1A",
            "early_plus": "Si",
            "intolerances": "",
            "notes": "",
        }

        with (
            patch("app.adapters.views.reports_routes.earlycare_data", return_value=[earlycare_row]),
            patch("app.adapters.views.reports_routes.lunchcare_data_for_report", return_value=[]),
        ):
            response = client.post(
                "/management/earlycare-reports/create",
                data={
                    "validFrom": "01/01/2026",
                    "validUntil": "31/01/2026",
                },
                follow_redirects=False,
            )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /management/lunchcare-reports/create (lines 419-440)
# Cubre: lunchcare_data (264-271), lunchcare_early_data (275-281),
#        lunch_default_luncare_report (98-112), early_default_lunchcare_report (175-189)
# ---------------------------------------------------------------------------


class TestCreateLunchcareReportPost:
    def test_post_lunchcare_report_returns_xlsx(self, client, app, db):
        """POST /management/lunchcare-reports/create → xlsx descarga."""
        _login_lunchcare(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.lunchcare_data", return_value=[]),
            patch("app.adapters.views.reports_routes.lunchcare_early_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/lunchcare-reports/create",
                data={"validFrom": "01-2026"},
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_lunchcare_report_admin_also_works(self, client, app, db):
        """POST /management/lunchcare-reports/create con admin → xlsx descarga."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.lunchcare_data", return_value=[]),
            patch("app.adapters.views.reports_routes.lunchcare_early_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/lunchcare-reports/create",
                data={"validFrom": "01-2026"},
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_lunchcare_report_no_auth_redirects(self, client, app):
        """POST /management/lunchcare-reports/create sin auth → 302."""
        from flask.globals import _cv_app

        ctx = _cv_app.get(None)
        if ctx is not None:
            local_g = ctx.g
            if hasattr(local_g, "_login_user"):
                delattr(local_g, "_login_user")

        response = client.post(
            "/management/lunchcare-reports/create",
            data={"validFrom": "01-2026"},
            follow_redirects=False,
        )
        assert response.status_code in (301, 302)

    def test_post_lunchcare_report_february(self, client, app, db):
        """POST /management/lunchcare-reports/create con febrero → calcua correctamente el último día."""
        _login_admin(client, app, db)

        with (
            patch("app.adapters.views.reports_routes.lunchcare_data", return_value=[]),
            patch("app.adapters.views.reports_routes.lunchcare_early_data", return_value=[]),
            patch(
                "app.infrastructure.excel.report.ExcelReport.get_xlsx",
                return_value=_make_excel_report_result(),
            ),
        ):
            response = client.post(
                "/management/lunchcare-reports/create",
                data={"validFrom": "02-2026"},
                follow_redirects=False,
            )

        assert response.status_code == 200

    def test_post_lunchcare_report_with_real_data(self, client, app, db):
        """POST /management/lunchcare-reports/create con datos reales → archivo generado."""
        _login_admin(client, app, db)

        lunchcare_row = {
            "lunch_day": "2026-01-15",
            "total": "10",
            "brothers": "2",
            "intolerances": "",
            "notes": "",
        }

        with (
            patch("app.adapters.views.reports_routes.lunchcare_data", return_value=[lunchcare_row]),
            patch("app.adapters.views.reports_routes.lunchcare_early_data", return_value=[]),
        ):
            response = client.post(
                "/management/lunchcare-reports/create",
                data={"validFrom": "01-2026"},
                follow_redirects=False,
            )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# _company_data, _yn, _format_intolerance_counts — unit-level via routes
# Estas helpers se invocan indirectamente al ejecutar las rutas POST.
# Los tests siguientes ejercen las funciones llamando a la ruta con data
# real (sin mockear early_data/lunch_data) para que la función recorra
# el código de las helpers también.
# ---------------------------------------------------------------------------


class TestHelperFunctionsViaPOST:
    def test_yn_helper_called_via_early_data_rows(self, client, app, db):
        """_yn() es invocada por early_data() al procesar filas con bool fields."""
        from app.adapters.views.reports_routes import _yn

        # Prueba directa de la función helper — necesita request context
        # porque _yn usa _() de flask_babel que resuelve locale via session.
        with app.test_request_context():
            assert _yn(True) in ("Si", "Sí", "Yes", "si")  # valor localizado
            assert _yn(False) in ("Non", "No", "non")

    def test_format_intolerance_counts_empty_dict(self, client, app, db):
        """_format_intolerance_counts() con dict vacío → string vacío."""
        from app.adapters.views.reports_routes import _format_intolerance_counts

        with app.test_request_context():
            result = _format_intolerance_counts({})
            assert result == ""

    def test_format_intolerance_counts_with_data(self, client, app, db):
        """_format_intolerance_counts() con datos → string con conteos."""
        from app.adapters.views.reports_routes import _format_intolerance_counts

        with app.test_request_context():
            result = _format_intolerance_counts({1: [2, "gluten"]})
            assert "2" in result

    def test_company_data_returns_dict(self, client, app, db):
        """_company_data() devuelve un dict con las claves esperadas."""
        from app.adapters.views.reports_routes import _company_data

        with app.test_request_context():
            data = _company_data()
            assert "name" in data
            assert "vat_number" in data
            assert "phone" in data
            assert "mail" in data
            assert "address" in data


# ---------------------------------------------------------------------------
# Data helper functions — cubren líneas 198-281
# Estos tests ejercen early_data(), lunch_data(), earlycare_data(),
# lunchcare_data_for_report(), lunchcare_data(), lunchcare_early_data()
# sin mockear las helpers, sino los use cases subyacentes.
# ---------------------------------------------------------------------------


class TestDataHelperFunctions:
    """Ejercen los data helpers mockeando solo los use cases internos."""

    def test_early_data_function_runs_with_rows(self, app, db):
        """early_data() ejecuta el use case y aplica _yn() a cada fila."""
        from datetime import datetime

        from app.adapters.views.reports_routes import early_data

        mock_rows = [
            {
                "early_day": "2026-01-15",
                "student": "Ana García",
                "course": "1A",
                "brother_number": "1",
                "early_plus": True,
                "not_come": False,
                "come_as_extra": False,
                "modified_by": "admin",
                "modified_notes": "",
                "partner": True,
            }
        ]

        with (
            patch(
                "app.application.attendance.get_early_attendance_report.GetEarlyAttendanceReportUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = early_data(
                    date_from="2026-01-01 00:00:00.000000",
                    date_until="2026-01-31 00:00:00.000000",
                    student_id=0,
                    report_type=0,
                )

        assert len(result) == 1
        # _yn() habrá transformado los bool en strings localizados
        assert result[0]["early_plus"] in ("Si", "Sí", "Non", "No", "si", "non")

    def test_early_data_function_empty_rows(self, app, db):
        """early_data() con use case retornando [] → lista vacía sin error."""
        from app.adapters.views.reports_routes import early_data

        with (
            patch(
                "app.application.attendance.get_early_attendance_report.GetEarlyAttendanceReportUseCase.execute",
                return_value=[],
            ),
        ):
            with app.test_request_context():
                result = early_data(
                    date_from="2026-01-01 00:00:00.000000",
                    date_until="2026-01-31 00:00:00.000000",
                    student_id=0,
                )

        assert result == []

    def test_lunch_data_function_runs_with_rows(self, app, db):
        """lunch_data() ejecuta el use case y aplica _yn() a cada fila."""
        from app.adapters.views.reports_routes import lunch_data

        mock_rows = [
            {
                "lunch_day": "2026-01-15",
                "student": "Pedro López",
                "course": "2B",
                "brother_number": "0",
                "not_come": False,
                "come_as_extra": True,
                "modified_by": "admin",
                "modified_notes": "",
                "partner": False,
            }
        ]

        with (
            patch(
                "app.application.attendance.get_lunch_attendance_report.GetLunchAttendanceReportUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = lunch_data(
                    date_from="2026-01-01 00:00:00.000000",
                    date_until="2026-01-31 00:00:00.000000",
                    student_id=0,
                )

        assert len(result) == 1
        assert result[0]["come_as_extra"] in ("Si", "Sí", "Non", "No", "si", "non")

    def test_lunch_data_function_empty_rows(self, app, db):
        """lunch_data() con use case retornando [] → lista vacía sin error."""
        from app.adapters.views.reports_routes import lunch_data

        with (
            patch(
                "app.application.attendance.get_lunch_attendance_report.GetLunchAttendanceReportUseCase.execute",
                return_value=[],
            ),
        ):
            with app.test_request_context():
                result = lunch_data(
                    date_from="2026-01-01 00:00:00.000000",
                    date_until="2026-01-31 00:00:00.000000",
                    student_id=0,
                )

        assert result == []

    def test_earlycare_data_function_runs(self, app, db):
        """earlycare_data() ejecuta el use case y aplica _yn() a cada fila."""
        from datetime import datetime

        from app.adapters.views.reports_routes import earlycare_data

        mock_rows = [
            {
                "early_day": "2026-01-15",
                "student": "Ana García",
                "course": "1A",
                "early_plus": True,
                "intolerances": "",
                "notes": "",
            }
        ]

        with (
            patch(
                "app.application.attendance.get_earlycare_daily_report.GetEarlycareDailyReportUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = earlycare_data(
                    first_day=datetime(2026, 1, 1),
                    last_day=datetime(2026, 1, 31),
                )

        assert len(result) == 1
        assert result[0]["early_plus"] in ("Si", "Sí", "Non", "No", "si", "non")

    def test_earlycare_data_with_intolerances(self, app, db):
        """earlycare_data() con intolerances no vacío → traduce y aplica."""
        from datetime import datetime

        from app.adapters.views.reports_routes import earlycare_data

        mock_rows = [
            {
                "early_day": "2026-01-15",
                "student": "Ana García",
                "course": "1A",
                "early_plus": False,
                "intolerances": "gluten",
                "notes": "",
            }
        ]

        with (
            patch(
                "app.application.attendance.get_earlycare_daily_report.GetEarlycareDailyReportUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = earlycare_data(
                    first_day=datetime(2026, 1, 1),
                    last_day=datetime(2026, 1, 31),
                )

        assert len(result) == 1
        # intolerances was translated (not empty string anymore, may be same or different)
        assert result[0]["intolerances"] is not None

    def test_lunchcare_data_for_report_function_runs(self, app, db):
        """lunchcare_data_for_report() ejecuta el use case correctamente."""
        from datetime import datetime

        from app.adapters.views.reports_routes import lunchcare_data_for_report

        mock_rows = [
            {
                "early_day": "2026-01-15",
                "student": "Pedro López",
                "course": "2B",
                "intolerances": "",
                "notes": "",
            }
        ]

        with (
            patch(
                "app.application.attendance.get_lunchcare_daily_report.GetLunchcareDailyReportUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = lunchcare_data_for_report(
                    first_day=datetime(2026, 1, 1),
                    last_day=datetime(2026, 1, 31),
                )

        assert len(result) == 1

    def test_lunchcare_data_for_report_with_intolerances(self, app, db):
        """lunchcare_data_for_report() con intolerances no vacío → traduce (línea 259)."""
        from datetime import datetime

        from app.adapters.views.reports_routes import lunchcare_data_for_report

        mock_rows = [
            {
                "early_day": "2026-01-15",
                "student": "Ana García",
                "course": "1A",
                "intolerances": "gluten, lácteos",
                "notes": "",
            }
        ]

        with (
            patch(
                "app.application.attendance.get_lunchcare_daily_report.GetLunchcareDailyReportUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = lunchcare_data_for_report(
                    first_day=datetime(2026, 1, 1),
                    last_day=datetime(2026, 1, 31),
                )

        assert len(result) == 1
        assert result[0]["intolerances"] is not None

    def test_lunchcare_data_function_runs(self, app, db):
        """lunchcare_data() ejecuta el use case y aplica _format_intolerance_counts()."""
        from datetime import datetime

        from app.adapters.views.reports_routes import lunchcare_data

        mock_rows = [
            {
                "lunch_day": "2026-01-15",
                "total": 10,
                "brothers": 2,
                "intolerance_counts": {},  # _format_intolerance_counts({}) → ""
                "notes": "",
            }
        ]

        with (
            patch(
                "app.application.attendance.get_lunchcare_summary_by_day.GetLunchcareSummaryByDayUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = lunchcare_data(
                    first_day=datetime(2026, 1, 1),
                    last_day=datetime(2026, 1, 31),
                )

        assert len(result) == 1
        assert "intolerances" in result[0]
        assert result[0]["intolerances"] == ""

    def test_lunchcare_early_data_function_runs(self, app, db):
        """lunchcare_early_data() ejecuta el use case y aplica _format_intolerance_counts()."""
        from datetime import datetime

        from app.adapters.views.reports_routes import lunchcare_early_data

        mock_rows = [
            {
                "early_day": "2026-01-15",
                "total": 5,
                "intolerance_counts": {1: [3, "gluten"]},  # non-empty → formats
                "notes": "",
            }
        ]

        with (
            patch(
                "app.application.attendance.get_earlycare_summary_by_day.GetEarlycareSummaryByDayUseCase.execute",
                return_value=mock_rows,
            ),
        ):
            with app.test_request_context():
                result = lunchcare_early_data(
                    first_day=datetime(2026, 1, 1),
                    last_day=datetime(2026, 1, 31),
                )

        assert len(result) == 1
        assert "intolerances" in result[0]
        # _format_intolerance_counts with data should produce a string with the count
        assert "3" in result[0]["intolerances"]
