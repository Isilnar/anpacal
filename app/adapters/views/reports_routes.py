# reports_routes.py — Adapter: blueprints para xeración de informes.
#
# Tres blueprints nun mesmo arquivo:
#   reports_bp           → /management/reports         (@admin_required)
#   earlycare_reports_bp → /management/earlycare-reports (@login_required)
#   lunchcare_reports_bp → /management/lunchcare-reports (@login_required)
#
# Lóxica + helpers migrados a use cases de aplicación (Strangler Fig, Fase C).

import calendar
import datetime

from flask import Blueprint, redirect, render_template, request, send_file, url_for
from flask_babel import _
from flask_login import login_required

from app.adapters.decorators import admin_required
from app.adapters.intolerance_translations import translate_intolerance
from app.application.attendance.get_early_attendance_report import GetEarlyAttendanceReportUseCase
from app.application.attendance.get_earlycare_daily_report import GetEarlycareDailyReportUseCase
from app.application.attendance.get_earlycare_summary_by_day import GetEarlycareSummaryByDayUseCase
from app.application.attendance.get_lunch_attendance_report import GetLunchAttendanceReportUseCase
from app.application.attendance.get_lunchcare_daily_report import GetLunchcareDailyReportUseCase
from app.application.attendance.get_lunchcare_summary_by_day import GetLunchcareSummaryByDayUseCase
from app.application.student.list_students import ListStudentsUseCase
from app.application.user.list_users import ListUsersUseCase
from app.infrastructure.attendance.repository import (
    SQLAlchemyEarlyRepository,
    SQLAlchemyLunchRepository,
)
from app.infrastructure.excel.report import ExcelReport
from app.infrastructure.intolerance.repository import SQLAlchemyDietIntoleranceRepository
from app.infrastructure.school_course.repository import SQLAlchemySchoolCourseRepository
from app.infrastructure.student.repository import SQLAlchemyStudentRepository
from app.infrastructure.user.repository import SQLAlchemyUserRepository

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------

reports_bp = Blueprint("reports_bp", __name__, url_prefix="/management/reports")
earlycare_reports_bp = Blueprint("earlycare_reports_bp", __name__, url_prefix="/management/earlycare-reports")
lunchcare_reports_bp = Blueprint("lunchcare_reports_bp", __name__, url_prefix="/management/lunchcare-reports")


# ---------------------------------------------------------------------------
# Adapter helpers — locale-aware label formatters
# ---------------------------------------------------------------------------


def _yn(value: bool) -> str:
    """Convert a boolean to a localised yes/no label."""
    return _("Si") if value else _("Non")


def _format_intolerance_counts(counts: dict) -> str:
    """Build a localised intolerance summary string from a raw counts dict.

    counts format: {intolerance_id: [count, description_gl]}
    Example output (ES): "2 alergia/s gluten, 1 alergia/s lácteos"
    """
    label = _("alerxia/s")
    parts = []
    for _id, (count, desc_gl) in counts.items():
        translated = translate_intolerance(desc_gl).lower()
        parts.append(f"{count} {label} {translated}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Table config functions (inlined from app/classes/utils.py)
# ---------------------------------------------------------------------------


def lunch_default_report():
    table_defaults = {
        "title": _("Comedor"),
        "datetime_format": ["%H:%M:%S", "%d/%m/%Y"],
        "subtitle": [_("Datos de"), _("obtidos ás"), _("do")],
        "header": [
            {"header_text": _("Data do rexistro"), "mapped_to": "lunch_day"},
            {"header_text": _("Alumno"), "mapped_to": "student"},
            {"header_text": _("Curso"), "mapped_to": "course"},
            {"header_text": _("Nº irmán"), "mapped_to": "brother_number"},
            {"header_text": _("Non se presentou"), "mapped_to": "not_come"},
            {"header_text": _("Foi de imprevisto"), "mapped_to": "come_as_extra"},
            {"header_text": _("Modificado por"), "mapped_to": "modified_by"},
            {"header_text": _("Notas"), "mapped_to": "modified_notes"},
            {"header_text": _("Socio"), "mapped_to": "partner"},
        ],
        "default_empty": _("Desconocido"),
    }

    return table_defaults


def lunch_default_luncare_report():
    table_defaults = {
        "title": _("Comedor"),
        "datetime_format": ["%H:%M:%S", "%d/%m/%Y"],
        "subtitle": [_("Datos de"), _("obtidos ás"), _("do")],
        "header": [
            {"header_text": _("Data"), "mapped_to": "lunch_day"},
            {"header_text": _("Total menús"), "mapped_to": "total"},
            {"header_text": _("Irmáns"), "mapped_to": "brothers"},
            {"header_text": _("Alerxias"), "mapped_to": "intolerances"},
            {"header_text": _("Notas"), "mapped_to": "notes"},
        ],
        "default_empty": _("Desconocido"),
    }

    return table_defaults


def early_default_report():
    table_defaults = {
        "title": _("Madrugadores"),
        "datetime_format": ["%H:%M:%S", "%d/%m/%Y"],
        "subtitle": [_("Datos de"), _("obtidos ás"), _("do")],
        "header": [
            {"header_text": _("Data do rexistro"), "mapped_to": "early_day"},
            {"header_text": _("Alumno"), "mapped_to": "student"},
            {"header_text": _("Curso"), "mapped_to": "course"},
            {"header_text": _("Nº irmán"), "mapped_to": "brother_number"},
            {"header_text": _("Con almorzo"), "mapped_to": "early_plus"},
            {"header_text": _("Non se presentou"), "mapped_to": "not_come"},
            {"header_text": _("Foi de imprevisto"), "mapped_to": "come_as_extra"},
            {"header_text": _("Modificado por"), "mapped_to": "modified_by"},
            {"header_text": _("Notas"), "mapped_to": "modified_notes"},
            {"header_text": _("Socio"), "mapped_to": "partner"},
        ],
        "default_empty": _("Desconocido"),
    }

    return table_defaults


def early_default_earlycare_report():
    table_defaults = {
        "title": _("Madrugadores"),
        "datetime_format": ["%H:%M:%S", "%d/%m/%Y"],
        "subtitle": [_("Datos de"), _("obtidos ás"), _("do")],
        "header": [
            {"header_text": _("Data"), "mapped_to": "early_day"},
            {"header_text": _("Alumno"), "mapped_to": "student"},
            {"header_text": _("Curso"), "mapped_to": "course"},
            {"header_text": _("Con Almorzo"), "mapped_to": "early_plus"},
            {"header_text": _("Alerxias"), "mapped_to": "intolerances"},
            {"header_text": _("Notas"), "mapped_to": "notes"},
        ],
        "default_empty": _("Desconocido"),
    }

    return table_defaults


def lunch_default_earlycare_report():
    table_defaults = {
        "title": _("Madrugadores"),
        "datetime_format": ["%H:%M:%S", "%d/%m/%Y"],
        "subtitle": [_("Datos de"), _("obtidos ás"), _("do")],
        "header": [
            {"header_text": _("Data"), "mapped_to": "early_day"},
            {"header_text": _("Total almorzos"), "mapped_to": "total"},
            {"header_text": _("Alerxias"), "mapped_to": "intolerances"},
            {"header_text": _("Notas"), "mapped_to": "notes"},
        ],
        "default_empty": _("Desconocido"),
    }

    return table_defaults


def early_default_lunchcare_report():
    table_defaults = {
        "title": _("Comedor"),
        "datetime_format": ["%H:%M:%S", "%d/%m/%Y"],
        "subtitle": [_("Datos de"), _("obtidos ás"), _("do")],
        "header": [
            {"header_text": _("Data"), "mapped_to": "lunch_day"},
            {"header_text": _("Alumno"), "mapped_to": "student"},
            {"header_text": _("Curso"), "mapped_to": "course"},
            {"header_text": _("Alerxias"), "mapped_to": "intolerances"},
            {"header_text": _("Notas"), "mapped_to": "notes"},
        ],
        "default_empty": _("Desconocido"),
    }

    return table_defaults


# ---------------------------------------------------------------------------
# Private data helpers — delegated to use cases
# ---------------------------------------------------------------------------


def early_data(date_from, date_until, student_id, report_type=0):
    rows = GetEarlyAttendanceReportUseCase(
        early_repo=SQLAlchemyEarlyRepository(),
        student_repo=SQLAlchemyStudentRepository(),
        course_repo=SQLAlchemySchoolCourseRepository(),
        user_repo=SQLAlchemyUserRepository(),
    ).execute(
        date_from=date_from,
        date_until=date_until,
        student_id=student_id,
        report_type=report_type,
    )
    for row in rows:
        row["not_come"] = _yn(row["not_come"])
        row["come_as_extra"] = _yn(row["come_as_extra"])
        row["early_plus"] = _yn(row["early_plus"])
        row["partner"] = _yn(row["partner"])
    return rows


def lunch_data(date_from, date_until, student_id):
    rows = GetLunchAttendanceReportUseCase(
        lunch_repo=SQLAlchemyLunchRepository(),
        student_repo=SQLAlchemyStudentRepository(),
        course_repo=SQLAlchemySchoolCourseRepository(),
        user_repo=SQLAlchemyUserRepository(),
    ).execute(
        date_from=date_from,
        date_until=date_until,
        student_id=student_id,
    )
    for row in rows:
        row["not_come"] = _yn(row["not_come"])
        row["come_as_extra"] = _yn(row["come_as_extra"])
        row["partner"] = _yn(row["partner"])
    return rows


def earlycare_data(first_day, last_day):
    rows = GetEarlycareDailyReportUseCase(
        early_repo=SQLAlchemyEarlyRepository(),
        student_repo=SQLAlchemyStudentRepository(),
        course_repo=SQLAlchemySchoolCourseRepository(),
        intolerance_repo=SQLAlchemyDietIntoleranceRepository(),
    ).execute(first_day=first_day, last_day=last_day)
    for row in rows:
        row["early_plus"] = _("Si") if row["early_plus"] else ""
        if row["intolerances"]:
            # get_string_for_student returns comma-joined GL descriptions — translate each token
            row["intolerances"] = ", ".join(translate_intolerance(t.strip()) for t in row["intolerances"].split(","))
    return rows


def lunchcare_data_for_report(first_day, last_day):
    rows = GetLunchcareDailyReportUseCase(
        lunch_repo=SQLAlchemyLunchRepository(),
        student_repo=SQLAlchemyStudentRepository(),
        course_repo=SQLAlchemySchoolCourseRepository(),
        intolerance_repo=SQLAlchemyDietIntoleranceRepository(),
    ).execute(first_day=first_day, last_day=last_day)
    for row in rows:
        if row["intolerances"]:
            row["intolerances"] = ", ".join(translate_intolerance(t.strip()) for t in row["intolerances"].split(","))
    return rows


def lunchcare_data(first_day, last_day):
    rows = GetLunchcareSummaryByDayUseCase(
        lunch_repo=SQLAlchemyLunchRepository(),
        student_repo=SQLAlchemyStudentRepository(),
        intolerance_repo=SQLAlchemyDietIntoleranceRepository(),
    ).execute(first_day=first_day, last_day=last_day)
    for row in rows:
        row["intolerances"] = _format_intolerance_counts(row.pop("intolerance_counts"))
    return rows


def lunchcare_early_data(first_day, last_day):
    rows = GetEarlycareSummaryByDayUseCase(
        early_repo=SQLAlchemyEarlyRepository(),
        intolerance_repo=SQLAlchemyDietIntoleranceRepository(),
    ).execute(first_day=first_day, last_day=last_day)
    for row in rows:
        row["intolerances"] = _format_intolerance_counts(row.pop("intolerance_counts"))
    return rows


# ---------------------------------------------------------------------------
# reports_bp — GET / + POST /create
# ---------------------------------------------------------------------------


def _company_data() -> dict:
    """Build company_data dict from app config — single source of truth."""
    from flask import current_app

    cfg = current_app.config
    return {
        "vat_number": cfg.get("COMPANY_VAT", ""),
        "name": cfg.get("COMPANY_NAME", ""),
        "phone": cfg.get("COMPANY_PHONE", ""),
        "mail": cfg.get("COMPANY_MAIL", ""),
        "address": cfg.get("COMPANY_ADDRESS", ""),
    }


@reports_bp.route("/")
@login_required
@admin_required
def management_reports():
    users_list = ListUsersUseCase(SQLAlchemyUserRepository()).execute()
    student_list = ListStudentsUseCase(SQLAlchemyStudentRepository()).execute()

    return render_template("station/management/get_reports.html", users_list=users_list, student_list=student_list)


@reports_bp.route("/create", methods=["GET"])
@login_required
@admin_required
def create_report_get():
    """GET /create — redirige ao formulario. Evita 405 cando o browser
    volve atrás despois de descargar un informe (POST → descarga → Atrás → GET)."""
    return redirect(url_for("reports_bp.management_reports"))


@reports_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_report_post():
    frm = request.form
    student_uid = int(frm.get("student"))
    report_type = int(frm.get("reportType"))
    date_from = datetime.datetime.strptime(frm.get("validFrom"), "%d/%m/%Y")
    date_from = datetime.datetime.strftime(date_from, "%Y-%m-%d") + " 00:00:00.000000"
    date_until = datetime.datetime.strptime(frm.get("validUntil"), "%d/%m/%Y")
    date_until = datetime.datetime.strftime(date_until, "%Y-%m-%d") + " 00:00:00.000000"

    company_data = _company_data()

    table_defaults = []
    events_data = []
    if report_type == 0:
        table_defaults.append(early_default_report())
        table_defaults.append(lunch_default_report())
        events_data.append(early_data(date_from, date_until, student_uid))
        events_data.append(lunch_data(date_from, date_until, student_uid))
    elif report_type == 1 or report_type == 2:
        table_defaults.append(early_default_report())
        events_data.append(early_data(date_from, date_until, student_uid, report_type))
    elif report_type == 3:
        table_defaults.append(lunch_default_report())
        events_data.append(lunch_data(date_from, date_until, student_uid))

    report = ExcelReport()
    report_file = report.get_xlsx(company_data=company_data, table_defaults=table_defaults, events_data=events_data)

    return send_file(report_file.get("file_data"), download_name=report_file.get("filename"), as_attachment=True)


# ---------------------------------------------------------------------------
# earlycare_reports_bp — GET / + POST /create
# ---------------------------------------------------------------------------


@earlycare_reports_bp.route("/")
@login_required
def management_earlycare_reports():
    return render_template("station/management/get_earlycare_reports.html")


@earlycare_reports_bp.route("/create", methods=["GET"])
@login_required
def create_earlycare_report_get():
    """GET /create — redirixe ao formulario para evitar 405 ao volver atrás."""
    return redirect(url_for("earlycare_reports_bp.management_earlycare_reports"))


@earlycare_reports_bp.route("/create", methods=["POST"])
@login_required
def create_earlycare_report_post():
    frm = request.form
    first_day = datetime.datetime.strptime(frm.get("validFrom"), "%d/%m/%Y")
    last_day = datetime.datetime.strptime(frm.get("validUntil"), "%d/%m/%Y")

    company_data = _company_data()

    table_defaults = []
    events_data = []

    table_defaults.append(early_default_earlycare_report())
    table_defaults.append(early_default_lunchcare_report())

    events_data.append(earlycare_data(first_day, last_day))
    events_data.append(lunchcare_data_for_report(first_day, last_day))

    report = ExcelReport()
    report_file = report.get_xlsx(company_data=company_data, table_defaults=table_defaults, events_data=events_data)

    return send_file(report_file.get("file_data"), download_name=report_file.get("filename"), as_attachment=True)


# ---------------------------------------------------------------------------
# lunchcare_reports_bp — GET / + POST /create
# ---------------------------------------------------------------------------


@lunchcare_reports_bp.route("/")
@login_required
def management_lunchcare_reports():
    return render_template("station/management/get_lunchcare_reports.html")


@lunchcare_reports_bp.route("/create", methods=["GET"])
@login_required
def create_lunchcare_report_get():
    """GET /create — redirixe ao formulario para evitar 405 ao volver atrás."""
    return redirect(url_for("lunchcare_reports_bp.management_lunchcare_reports"))


@lunchcare_reports_bp.route("/create", methods=["POST"])
@login_required
def create_lunchcare_report_post():
    frm = request.form
    month_year = frm.get("validFrom").split("-")
    first_day = datetime.datetime.strptime(f"01/{month_year[0]}/{month_year[1]}", "%d/%m/%Y")
    last_day = datetime.datetime.strptime(
        f"{calendar.monthrange(int(month_year[1]), int(month_year[0]))[1]}/{month_year[0]}/{month_year[1]}", "%d/%m/%Y"
    )

    company_data = _company_data()

    table_defaults = []
    events_data = []

    table_defaults.append(lunch_default_luncare_report())
    table_defaults.append(lunch_default_earlycare_report())

    events_data.append(lunchcare_data(first_day, last_day))
    events_data.append(lunchcare_early_data(first_day, last_day))

    report = ExcelReport()
    report_file = report.get_xlsx(company_data=company_data, table_defaults=table_defaults, events_data=events_data)

    return send_file(report_file.get("file_data"), download_name=report_file.get("filename"), as_attachment=True)
