import secrets
from datetime import datetime as _dt
from datetime import timedelta as _td

import pytz as _pytz
from flask import current_app
from flask_login import current_user


def get_random_password(pass_len=8):
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    p = "".join(secrets.choice(s) for _ in range(pass_len))

    return p


def get_current_schools(selected_user=None):
    from app.application.school.list_schools_with_selection import ListSchoolsWithSelectionUseCase
    from app.infrastructure.school.repository import SQLAlchemySchoolRepository

    user_id = selected_user.id if selected_user is not None else None
    return ListSchoolsWithSelectionUseCase(SQLAlchemySchoolRepository()).execute(user_id)


def get_selected_roles(selected_user=None):
    # MIGRATED: rewritten using ListRolesUseCase (Clean Architecture)
    from app.adapters.intolerance_translations import translate_role
    from app.application.role.list_roles import ListRolesUseCase
    from app.infrastructure.role.repository import SQLAlchemyRoleRepository

    user_id = selected_user.id if selected_user is not None else None
    result = ListRolesUseCase(SQLAlchemyRoleRepository(), user_id).execute()
    # Adapter: convert is_selected (bool) → int 0/1 to preserve template contract
    # and translate description to the active locale.
    for item in result:
        item["is_selected"] = 1 if item["is_selected"] else 0
        item["description"] = translate_role(item["description"])
    return result


def get_selected_intolerances(selected_user=None):
    # MIGRATED: rewritten using ListDietIntolerancesUseCase (Clean Architecture)
    from app.adapters.intolerance_translations import translate_intolerance
    from app.application.intolerance.list_diet_intolerances import ListDietIntolerancesUseCase
    from app.infrastructure.intolerance.repository import SQLAlchemyDietIntoleranceRepository

    student_id = selected_user.id if selected_user is not None else None
    repo = SQLAlchemyDietIntoleranceRepository()
    use_case = ListDietIntolerancesUseCase(repo, student_id)
    result = use_case.execute()
    # Adapter: rename 'selected' (bool) → 'is_selected' (int 0/1) to preserve template contract
    # and translate description to the active locale.
    for item in result:
        item["is_selected"] = 1 if item.pop("selected") else 0
        item["description"] = translate_intolerance(item["description"])
    return result


# ---------------------------------------------------------------------------
# Calendar utility functions (migrated from app/classes/utils.py — Ciclo C)
# ---------------------------------------------------------------------------


def get_calendar_events(current_start_date, center_id):
    current_datetime = _dt.strptime(current_start_date, "%Y-%m-%d")
    student_ids = [s.student.id for s in current_user.students if int(s.student.school_id) == int(center_id)]
    from app.application.attendance.get_calendar_events_by_students import GetCalendarEventsByStudentsUseCase
    from app.infrastructure.attendance.repository import SQLAlchemyEarlyRepository, SQLAlchemyLunchRepository

    use_case = GetCalendarEventsByStudentsUseCase(
        SQLAlchemyEarlyRepository(),
        SQLAlchemyLunchRepository(),
    )
    return use_case.execute(student_ids, current_datetime.date())


def get_disabled_dates():
    from app.application.holyday.list_holydays import ListHolydaysUseCase
    from app.infrastructure.holyday.repository import SQLAlchemyHolydayRepository

    holydays = ListHolydaysUseCase(SQLAlchemyHolydayRepository()).execute()
    return [h.holyday.strftime("%Y-%m-%d") for h in holydays]


def get_disabled_dates_reversed():
    from app.application.holyday.list_holydays import ListHolydaysUseCase
    from app.infrastructure.holyday.repository import SQLAlchemyHolydayRepository

    holydays = ListHolydaysUseCase(SQLAlchemyHolydayRepository()).execute()
    return [h.holyday.strftime("%d-%m-%Y") for h in holydays]


def get_calendar_start_date(time_limit=None, format=0):
    tz = _pytz.timezone("Europe/Madrid")
    if time_limit is None:
        try:
            time_limit = current_app.config.get("CALENDAR_EDIT_CUTOFF_TIME", (9, 15, 0, 0))
        except RuntimeError:
            time_limit = (9, 15, 0, 0)
    current_start_date = _dt.now(tz)
    limit_time = current_start_date.replace(
        hour=time_limit[0], minute=time_limit[1], second=time_limit[2], microsecond=time_limit[3]
    )
    if current_start_date > limit_time:
        current_start_date = current_start_date + _td(days=1)
    if format == 0:
        current_start_date = current_start_date.strftime("%Y-%m-%d")
    return current_start_date


def get_calendar_start_date_early_lunch(time_limit=None, format=0):
    current_start_date = _dt.now()
    if format == 0:
        current_start_date = current_start_date.strftime("%Y-%m-%d")
    return current_start_date


def get_dates_between(start, end):
    res = []
    star_date = _dt.strptime(start, "%Y-%m-%d")
    end_date = _dt.strptime(end, "%Y-%m-%d")
    while star_date < end_date:
        res.append(star_date.strftime("%Y-%m-%d"))
        star_date = star_date + _td(days=1)
    return res
