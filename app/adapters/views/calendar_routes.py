# adapters/views/calendar_routes.py
# Blueprint calendar_bp — rutas limpias para attendance.
# Convive con calendar_station (Strangler Fig).

from datetime import date, datetime

from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required

from app.application.attendance.get_calendar_events import GetCalendarEventsUseCase
from app.application.attendance.get_earlycare_stats import GetEarlycareStatsUseCase
from app.application.attendance.get_lunchcare_stats import GetLunchcareStatsUseCase
from app.application.attendance.save_attendance_range import (
    AttendanceItem,
    SaveAttendanceRangeDTO,
    SaveAttendanceRangeUseCase,
)
from app.infrastructure.attendance.repository import (
    SQLAlchemyEarlyRepository,
    SQLAlchemyLunchRepository,
)
from app.infrastructure.holyday.repository import SQLAlchemyHolydayRepository
from app.infrastructure.student.repository import SQLAlchemyStudentRepository

calendar_bp = Blueprint("calendar_bp", __name__, url_prefix="/calendar")


def _make_repos():
    return (
        SQLAlchemyEarlyRepository(),
        SQLAlchemyLunchRepository(),
        SQLAlchemyHolydayRepository(),
    )


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


# ---------------------------------------------------------------------------
# GET /calendar/events — GetCalendarEventsUseCase
# ---------------------------------------------------------------------------
@calendar_bp.route("/events", methods=["GET", "POST"])
@login_required
def get_calendar_events():
    data = request.get_json(silent=True) or request.args
    school_id = int(data.get("school_id", 0))
    day = _parse_date(data.get("date", ""))
    early_repo, lunch_repo, _ = _make_repos()
    use_case = GetCalendarEventsUseCase(early_repo, lunch_repo, SQLAlchemyStudentRepository())
    events = use_case.execute(school_id, day)
    result = [
        {
            "student_id": e["student_id"],
            "early_requested": e["early"].early_requested if e["early"] else 0,
            "early_plus_requested": e["early"].early_plus_requested if e["early"] else 0,
            "lunch_requested": e["lunch"].lunch_requested if e["lunch"] else 0,
        }
        for e in events
    ]
    return make_response(jsonify(result), 200)


# ---------------------------------------------------------------------------
# GET /calendar/earlycare-stats — GetEarlycareStatsUseCase
# ---------------------------------------------------------------------------
@calendar_bp.route("/earlycare-stats", methods=["GET", "POST"])
@login_required
def get_earlycare_stats():
    data = request.get_json(silent=True) or request.args
    school_id = int(data.get("school_id", 0))
    day = _parse_date(data.get("date", ""))
    early_repo, _, _ = _make_repos()
    stats = GetEarlycareStatsUseCase(early_repo).execute(school_id, day)
    return make_response(
        jsonify(
            {
                "total_requested": stats.total_requested,
                "total_plus_requested": stats.total_plus_requested,
                "total_as_extra": stats.total_as_extra,
                "total_not_come": stats.total_not_come,
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# GET /calendar/lunchcare-stats — GetLunchcareStatsUseCase
# ---------------------------------------------------------------------------
@calendar_bp.route("/lunchcare-stats", methods=["GET", "POST"])
@login_required
def get_lunchcare_stats():
    data = request.get_json(silent=True) or request.args
    school_id = int(data.get("school_id", 0))
    day = _parse_date(data.get("date", ""))
    _, lunch_repo, _ = _make_repos()
    stats = GetLunchcareStatsUseCase(lunch_repo).execute(school_id, day)
    return make_response(
        jsonify(
            {
                "total_requested": stats.total_requested,
                "total_as_extra": stats.total_as_extra,
                "total_not_come": stats.total_not_come,
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# POST /calendar/attendance-range — SaveAttendanceRangeUseCase
# ---------------------------------------------------------------------------
@calendar_bp.route("/attendance-range", methods=["POST"])
@login_required
def save_attendance_range():
    data = request.get_json(silent=True) or {}
    date_from_str = data.get("date_from", "")
    date_to_str = data.get("date_to", "")

    if not date_from_str or not date_to_str:
        return make_response(jsonify({"error": "date_from and date_to required"}), 422)

    date_from = _parse_date(date_from_str)
    date_to = _parse_date(date_to_str)

    if date_from > date_to:
        return make_response(jsonify({"error": "date_from must be <= date_to"}), 422)

    raw_attendances = data.get("attendances", [])
    items = [
        AttendanceItem(
            student_id=int(a["student_id"]),
            early_requested=int(a.get("early_requested", 0)),
            early_plus_requested=int(a.get("early_plus_requested", 0)),
            lunch_requested=int(a.get("lunch_requested", 0)),
            user_id=current_user.id,
        )
        for a in raw_attendances
    ]

    early_repo, lunch_repo, holyday_repo = _make_repos()
    dto = SaveAttendanceRangeDTO(
        school_id=int(data.get("school_id", 0)),
        date_from=date_from,
        date_to=date_to,
        attendances=items,
    )
    result = SaveAttendanceRangeUseCase(early_repo, lunch_repo, holyday_repo).execute(dto)

    return make_response(
        jsonify(
            {
                "saved_dates": [d.isoformat() for d in result.saved_dates],
                "skipped_dates": [d.isoformat() for d in result.skipped_dates],
            }
        ),
        200,
    )
