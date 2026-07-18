# calendar_station_routes.py — CA adapter: calendar station routes.
# Blueprint 'calendar_station' (no prefix) — name kept for template url_for compatibility.
#
# BOOTSTRAP-ORM: SQLAlchemy repositories and use cases are imported INSIDE
# each function body to defer ORM loading. Do NOT move them to module level.

from datetime import datetime

from flask import Blueprint, current_app, jsonify, make_response, render_template, request
from flask_babel import _, format_date, get_locale
from flask_login import current_user, login_required

from app.adapters.intolerance_translations import translate_intolerance_in_text
from app.adapters.utils import (
    get_calendar_events,
    get_calendar_start_date,
    get_calendar_start_date_early_lunch,
    get_dates_between,
    get_disabled_dates,
    get_disabled_dates_reversed,
)

calendar_station = Blueprint("calendar_station", __name__)


@calendar_station.route("/management_calendar")
@login_required
def management_calendar_post():
    from app.application.school.get_schools_by_ids import GetSchoolsByIdsUseCase
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    repo = SQLAlchemySchoolRepository()
    school_ids = [int(s.student.school_id) for s in current_user.students if s.student.school_id is not None]
    current_school_list = GetSchoolsByIdsUseCase(repo).execute(school_ids)

    if current_school_list is not None and len(current_school_list) == 1:
        center_id = current_school_list[0].id
        current_school = repo.get_by_id(center_id)
        current_date = get_calendar_start_date()
        current_start_date = current_app.config.get("SCHOOL_YEAR_START", "2024-09-01")
        current_events = get_calendar_events(current_start_date, center_id)
        disabled_dates = get_disabled_dates()
        disabled_dates_reverse = get_disabled_dates_reversed()
        disabled_calendar_dates = get_dates_between(current_start_date, current_date)

        return render_template(
            "station/calendar/calendar.html",
            current_school=current_school,
            current_start_date=current_start_date,
            current_date=current_date,
            current_events=current_events,
            current_locale=get_locale(),
            disabled_dates=disabled_dates,
            disabled_dates_reverse=disabled_dates_reverse,
            disabled_calendar_dates=disabled_calendar_dates,
        )
    else:
        return render_template("station/calendar/calendar_list.html", centers_list=current_school_list)


@calendar_station.route("/management_earlycare_calendar")
@login_required
def management_earlycare_calendar_post():
    from app.application.school.get_schools_by_ids import GetSchoolsByIdsUseCase
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    repo = SQLAlchemySchoolRepository()
    school_ids = [s.school_id for s in current_user.schools]
    current_school_list = GetSchoolsByIdsUseCase(repo).execute(school_ids)

    if current_school_list is not None and len(current_school_list) == 1:
        center_id = current_school_list[0].id
        current_school = repo.get_by_id(center_id)
        current_start_date = get_calendar_start_date_early_lunch()
        current_events = get_calendar_events(current_start_date, center_id)
        return render_template(
            "station/calendar/earlycare_calendar.html",
            current_school=current_school,
            current_start_date=current_start_date,
            current_events=current_events,
            current_locale=get_locale(),
        )
    else:
        return render_template("station/calendar/calendar_list.html", centers_list=current_school_list)


@calendar_station.route("/management_earlycare_calendar", methods=["POST"])
@login_required
def management_earlycare_calendar():
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    frm = request.form
    center_id = frm.get("centerId")
    current_school = SQLAlchemySchoolRepository().get_by_id(int(center_id))
    current_start_date = get_calendar_start_date_early_lunch()
    current_events = get_calendar_events(current_start_date, center_id)
    return render_template(
        "station/calendar/calendar.html",
        current_school=current_school,
        current_start_date=current_start_date,
        current_events=current_events,
        current_locale=get_locale(),
    )


@calendar_station.route("/management_lunchcare_calendar")
@login_required
def management_lunchcare_calendar_post():
    from app.application.school.get_schools_by_ids import GetSchoolsByIdsUseCase
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    repo = SQLAlchemySchoolRepository()
    school_ids = [s.school_id for s in current_user.schools]
    current_school_list = GetSchoolsByIdsUseCase(repo).execute(school_ids)

    if current_school_list is not None and len(current_school_list) == 1:
        center_id = current_school_list[0].id
        current_school = repo.get_by_id(center_id)
        current_start_date = get_calendar_start_date_early_lunch()
        current_events = get_calendar_events(current_start_date, center_id)
        return render_template(
            "station/calendar/lunchcare_calendar.html",
            current_school=current_school,
            current_start_date=current_start_date,
            current_events=current_events,
            current_locale=get_locale(),
        )
    else:
        return render_template("station/calendar/calendar_list.html", centers_list=current_school_list)


@calendar_station.route("/management_lunchcare_calendar", methods=["POST"])
@login_required
def management_lunchcare_calendar():
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    frm = request.form
    center_id = frm.get("centerId")
    current_school = SQLAlchemySchoolRepository().get_by_id(int(center_id))
    current_start_date = get_calendar_start_date_early_lunch()
    current_events = get_calendar_events(current_start_date, center_id)
    return render_template(
        "station/calendar/calendar.html",
        current_school=current_school,
        current_start_date=current_start_date,
        current_events=current_events,
        current_locale=get_locale(),
    )


@calendar_station.route("/management_calendar", methods=["POST"])
@login_required
def management_calendar():
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    frm = request.form
    center_id = frm.get("centerId")
    current_school = SQLAlchemySchoolRepository().get_by_id(int(center_id))
    current_start_date = get_calendar_start_date()
    current_events = get_calendar_events(current_start_date, center_id)
    return render_template(
        "station/calendar/calendar.html",
        current_school=current_school,
        current_start_date=current_start_date,
        current_events=current_events,
        current_locale=get_locale(),
    )


@calendar_station.route("/load_calendar_event", methods=["POST"])
@login_required
def load_calendar_event():
    """Carga los datos de un día del calendario para el modal de familia."""
    from app.application.attendance.get_day_attendance_by_students import GetDayAttendanceByStudentsUseCase
    from app.infrastructure.attendance.repository import SQLAlchemyEarlyRepository, SQLAlchemyLunchRepository

    data = request.get_json()
    current_event_date = data["current_event_date"]
    center_id = int(data["center_id"])

    current_datetime = datetime.strptime(current_event_date, "%Y-%m-%d")
    current_day = current_datetime.date()

    # Alumnos del usuario vinculados al centro
    students = [s.student for s in current_user.students if int(s.student.school_id) == int(center_id)]

    event_data = {}
    event_data["current_date"] = current_datetime.strftime("%d/%m/%Y")

    # Fecha en gallego
    locale_date = format_date(current_datetime, "full").capitalize()
    # Reformatear meses al gallego
    _meses = {
        "enero": "xaneiro",
        "febrero": "febreiro",
        "marzo": "marzo",
        "abril": "abril",
        "mayo": "maio",
        "junio": "xuño",
        "julio": "xullo",
        "agosto": "agosto",
        "septiembre": "setembro",
        "octubre": "outubro",
        "noviembre": "novembro",
        "deciembre": "decembro",
        "monday": "luns",
        "tuesday": "martes",
        "wednesday": "mércores",
        "thursday": "xoves",
        "friday": "venres",
    }
    for es, gl in _meses.items():
        locale_date = locale_date.replace(es, gl)
    event_data["locale_date"] = locale_date

    student_ids = [s.id for s in students]
    uc_result = GetDayAttendanceByStudentsUseCase(SQLAlchemyEarlyRepository(), SQLAlchemyLunchRepository()).execute(
        student_ids, current_day
    )

    fullname_map = {s.id: s.name + " " + s.surname for s in students}
    current_students_data = [{**row, "fullname": fullname_map[row["id"]]} for row in uc_result]

    event_data["current_students_data"] = current_students_data
    return make_response(jsonify(event_data), 200)


@calendar_station.route("/save_calendar_event", methods=["POST"])
@login_required
def save_calendar_event():
    """Guarda los cambios del modal de calendario de familia."""
    from app.application.attendance.save_attendance_range import (
        AttendanceItem,
        SaveAttendanceRangeDTO,
        SaveAttendanceRangeUseCase,
    )
    from app.infrastructure.attendance.repository import SQLAlchemyEarlyRepository, SQLAlchemyLunchRepository
    from app.infrastructure.holyday.repository import SQLAlchemyHolydayRepository

    data = request.get_json()
    from_date_str = data.get("current_from_date", "")
    to_date_str = data.get("current_to_date", "")
    early_request = data.get("current_early_request", {})
    early_plus_request = data.get("current_early_plus_request", {})
    lunch_request = data.get("current_lunch_request", {})

    from_date = datetime.strptime(from_date_str, "%d/%m/%Y").date()
    to_date = datetime.strptime(to_date_str, "%d/%m/%Y").date()

    # Obtener el school_id del primer alumno vinculado al usuario
    school_id = 0
    if current_user.students:
        first_student = current_user.students[0].student
        school_id = int(first_student.school_id) if first_student.school_id else 0

    # Validar ownership: solo alumnos vinculados al usuario actual
    owned_student_ids = {str(s.student.id) for s in current_user.students}
    all_student_ids = set(early_request.keys()) | set(early_plus_request.keys()) | set(lunch_request.keys())
    unauthorised = all_student_ids - owned_student_ids
    if unauthorised:
        return make_response(jsonify({"error": "Algún alumno non pertence ao usuario"}), 403)

    # Construir los AttendanceItems combinando early + early_plus + lunch
    items = [
        AttendanceItem(
            student_id=int(sid),
            early_requested=int(early_request.get(sid, 0)),
            early_plus_requested=int(early_plus_request.get(sid, 0)),
            lunch_requested=int(lunch_request.get(sid, 0)),
            user_id=current_user.id,
        )
        for sid in all_student_ids
    ]

    dto = SaveAttendanceRangeDTO(
        school_id=school_id,
        date_from=from_date,
        date_to=to_date,
        attendances=items,
    )
    result = SaveAttendanceRangeUseCase(
        SQLAlchemyEarlyRepository(),
        SQLAlchemyLunchRepository(),
        SQLAlchemyHolydayRepository(),
    ).execute(dto)

    # Releer los eventos guardados para obtener el tipo real de cada fecha
    updated_events = get_calendar_events(from_date.strftime("%Y-%m-%d"), school_id)

    # Construir índice date_str → (event_type, date_compact) solo para fechas guardadas
    saved_set = {d.strftime("%Y-%m-%d") for d in result.saved_dates}
    event_dates = []
    for ev in updated_events:
        if ev[0] in saved_set:
            event_dates.append({"id": ev[2], "start": ev[0], "event_type": ev[1]})

    # También incluir las fechas guardadas donde el resultado es "sin servicio" (null)
    # — fechas que estaban en saved_dates pero no aparecen en updated_events
    dates_in_events = {e["start"] for e in event_dates}
    for d in result.saved_dates:
        d_str = d.strftime("%Y-%m-%d")
        if d_str not in dates_in_events:
            event_dates.append({"id": d.strftime("%Y%m%d"), "start": d_str, "event_type": None})

    return make_response(
        jsonify(
            {
                "event_dates": event_dates,
                "event_type": None,  # el JS usará event_dates[i].event_type en su lugar
                "saved_dates": [d.isoformat() for d in result.saved_dates],
                "skipped_dates": [d.isoformat() for d in result.skipped_dates],
            }
        ),
        200,
    )


@calendar_station.route("/load_earlycare_calendar_event", methods=["POST"])
@login_required
def load_earlycare_calendar_event():
    """Carga los datos de un día del calendario de madrugadores/comedor."""
    from app.application.attendance.get_care_calendar_event import GetCareCalendarEventUseCase
    from app.infrastructure.attendance.repository import SQLAlchemyEarlyRepository, SQLAlchemyLunchRepository
    from app.infrastructure.intolerance.repository import SQLAlchemyDietIntoleranceRepository
    from app.infrastructure.student.repository import SQLAlchemyStudentRepository

    data = request.get_json()
    current_event_date = data["current_event_date"]
    center_id = int(data["center_id"])

    current_datetime = datetime.strptime(current_event_date, "%Y-%m-%d")
    current_day = current_datetime.date()

    locale_date = format_date(current_datetime, "full").capitalize()
    _meses = {
        "enero": "xaneiro",
        "febrero": "febreiro",
        "marzo": "marzo",
        "abril": "abril",
        "mayo": "maio",
        "junio": "xuño",
        "julio": "xullo",
        "agosto": "agosto",
        "septiembre": "setembro",
        "octubre": "outubro",
        "noviembre": "novembro",
        "deciembre": "decembro",
        "monday": "luns",
        "tuesday": "martes",
        "wednesday": "mércores",
        "thursday": "xoves",
        "friday": "venres",
    }
    for es, gl in _meses.items():
        locale_date = locale_date.replace(es, gl)

    dto = GetCareCalendarEventUseCase(
        SQLAlchemyEarlyRepository(),
        SQLAlchemyLunchRepository(),
        SQLAlchemyStudentRepository(),
        SQLAlchemyDietIntoleranceRepository(),
    ).execute(center_id, current_day)

    # Traducir etiquetas de intolerancias (provienen del use case sin traducir)
    almuerzo_intol = (
        translate_intolerance_in_text(dto.almuerzo_intolerances.replace(" alerxia/s ", f" {_('alerxia/s')} "))
        if dto.almuerzo_intolerances
        else ""
    )
    comedor_intol = (
        translate_intolerance_in_text(dto.comedor_intolerances.replace(" alerxia/s ", f" {_('alerxia/s')} "))
        if dto.comedor_intolerances
        else ""
    )

    event_data = {
        "locale_date": locale_date,
        "lunchcare_almuerzo": f"{_('Madrugadores con almorzo')}: {dto.almuerzo_total}",
        "almorzo_infantil": f"{_('Infantil')}: {dto.almuerzo_infantil}",
        "almorzo_primaria": f"{_('Primaria')}: {dto.almuerzo_primaria}",
        "lunchcare_almuerzo_intolerances": almuerzo_intol,
        "lunchcare_comedor": f"{_('Comedor')}: {dto.comedor_total}",
        "comedor_infantil": f"{_('Infantil')}: {dto.comedor_infantil}",
        "comedor_primaria": f"{_('Primaria')}: {dto.comedor_primaria}",
        "lunchcare_comedor_intolerances": comedor_intol,
    }
    return make_response(jsonify(event_data), 200)


@calendar_station.route("/load_lunchcare_calendar_event", methods=["POST"])
@login_required
def load_lunchcare_calendar_event():
    """Carga los datos de un día del calendario de comedor/madrugadores."""
    from app.application.attendance.get_care_calendar_event import GetCareCalendarEventUseCase
    from app.infrastructure.attendance.repository import SQLAlchemyEarlyRepository, SQLAlchemyLunchRepository
    from app.infrastructure.intolerance.repository import SQLAlchemyDietIntoleranceRepository
    from app.infrastructure.student.repository import SQLAlchemyStudentRepository

    data = request.get_json()
    current_event_date = data["current_event_date"]
    center_id = int(data["center_id"])

    current_datetime = datetime.strptime(current_event_date, "%Y-%m-%d")
    current_day = current_datetime.date()

    locale_date = format_date(current_datetime, "full").capitalize()
    _meses = {
        "enero": "xaneiro",
        "febrero": "febreiro",
        "marzo": "marzo",
        "abril": "abril",
        "mayo": "maio",
        "junio": "xuño",
        "julio": "xullo",
        "agosto": "agosto",
        "septiembre": "setembro",
        "octubre": "outubro",
        "noviembre": "novembro",
        "deciembre": "decembro",
        "monday": "luns",
        "tuesday": "martes",
        "wednesday": "mércores",
        "thursday": "xoves",
        "friday": "venres",
    }
    for es, gl in _meses.items():
        locale_date = locale_date.replace(es, gl)

    dto = GetCareCalendarEventUseCase(
        SQLAlchemyEarlyRepository(),
        SQLAlchemyLunchRepository(),
        SQLAlchemyStudentRepository(),
        SQLAlchemyDietIntoleranceRepository(),
    ).execute(center_id, current_day)

    # Traducir etiquetas de intolerancias
    almuerzo_intol = (
        translate_intolerance_in_text(dto.almuerzo_intolerances.replace(" alerxia/s ", f" {_('alerxia/s')} "))
        if dto.almuerzo_intolerances
        else ""
    )
    comedor_intol = (
        translate_intolerance_in_text(dto.comedor_intolerances.replace(" alerxia/s ", f" {_('alerxia/s')} "))
        if dto.comedor_intolerances
        else ""
    )

    event_data = {
        "locale_date": locale_date,
        "lunchcare_almuerzo": f"{_('Madrugadores con almorzo')}: {dto.almuerzo_total}",
        "almorzo_infantil": f"{_('Infantil')}: {dto.almuerzo_infantil}",
        "almorzo_primaria": f"{_('Primaria')}: {dto.almuerzo_primaria}",
        "lunchcare_almuerzo_intolerances": almuerzo_intol,
        "lunchcare_comedor": f"{_('Comedor')}: {dto.comedor_total}",
        "comedor_infantil": f"{_('Infantil')}: {dto.comedor_infantil}",
        "comedor_primaria": f"{_('Primaria')}: {dto.comedor_primaria}",
        "lunchcare_comedor_intolerances": comedor_intol,
    }
    return make_response(jsonify(event_data), 200)
