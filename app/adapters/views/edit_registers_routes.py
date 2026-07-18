# edit_registers_routes.py — Adapter: blueprint para edición de rexistros.
#
# Blueprint 'edit_registers_bp' con prefijo '/management/edit'.
# Lóxica copiada verbatim de app/views/management.py (Strangler Fig, Fase B).
# Os fetch() en edit_registers.html usan URLs relativas — non precisan cambio.

import datetime

from flask import Blueprint, jsonify, make_response, render_template, request
from flask_babel import _
from flask_login import current_user, login_required

from app.adapters.decorators import admin_required
from app.application.attendance.get_attendance_by_id import GetAttendanceByIdUseCase
from app.application.attendance.save_single_attendance import (
    SaveSingleAttendanceDTO,
    SaveSingleAttendanceUseCase,
)
from app.application.attendance.search_attendance import (
    SearchAttendanceDTO,
    SearchAttendanceUseCase,
)
from app.application.student.list_students import ListStudentsUseCase
from app.application.user.list_users import ListUsersUseCase
from app.infrastructure.attendance.repository import (
    SQLAlchemyEarlyRepository,
    SQLAlchemyLunchRepository,
)
from app.infrastructure.student.repository import SQLAlchemyStudentRepository
from app.infrastructure.user.repository import SQLAlchemyUserRepository

edit_registers_bp = Blueprint("edit_registers_bp", __name__, url_prefix="/management/edit")


@edit_registers_bp.route("/")
@login_required
@admin_required
def management_edit():
    users_list = ListUsersUseCase(SQLAlchemyUserRepository()).execute()
    student_list = ListStudentsUseCase(SQLAlchemyStudentRepository()).execute()
    user_list = ListUsersUseCase(SQLAlchemyUserRepository()).execute()

    return render_template(
        "station/management/edit_registers.html",
        users_list=users_list,
        student_list=student_list,
        user_list=user_list,
    )


@edit_registers_bp.route("/get_register_data_post", methods=["POST"])
@login_required
@admin_required
def get_register_data_post():
    register_type = request.json["register_type"]
    register_id = int(request.json["register_id"])

    use_case = GetAttendanceByIdUseCase(
        early_repo=SQLAlchemyEarlyRepository(),
        lunch_repo=SQLAlchemyLunchRepository(),
        student_repo=SQLAlchemyStudentRepository(),
    )
    res = use_case.execute(attendance_id=register_id, attendance_type=register_type)

    # Traducir type_text para que el frontend muestre el idioma activo
    if res.get("type_text"):
        res["type_text"] = _(res["type_text"])

    return make_response(jsonify(res), 200)


@edit_registers_bp.route("/find_registers_post", methods=["POST"])
@login_required
@admin_required
def find_registers_post():
    register_type = int(request.json["register_type"])
    register_student = int(request.json["register_student"])
    register_user = int(request.json["register_user"])

    register_from = datetime.datetime.strptime(request.json["register_from"], "%d/%m/%Y")
    date_from = datetime.datetime.strftime(register_from, "%Y-%m-%d")
    register_until = datetime.datetime.strptime(request.json["register_until"], "%d/%m/%Y")
    date_until = datetime.datetime.strftime(register_until, "%Y-%m-%d")

    dto = SearchAttendanceDTO(
        register_type=register_type,
        register_student=register_student,
        register_user=register_user,
        date_from=date_from,
        date_until=date_until,
    )

    use_case = SearchAttendanceUseCase(
        early_repo=SQLAlchemyEarlyRepository(),
        lunch_repo=SQLAlchemyLunchRepository(),
        student_repo=SQLAlchemyStudentRepository(),
        user_repo=SQLAlchemyUserRepository(),
    )
    sorted_list = use_case.execute(dto)

    return make_response(jsonify(sorted_list), 200)


@edit_registers_bp.route("/save_registers_post", methods=["POST"])
@login_required
@admin_required
def save_registers_post():
    frm = request.json
    student_uid = int(frm.get("student_value"))
    report_type = int(frm.get("type_value"))
    register_id = int(frm.get("id"))
    register_date = datetime.datetime.strptime(frm.get("date_value"), "%d/%m/%Y").date()
    register_notes = frm.get("register_notes")
    register_extra = frm.get("extra")
    register_not_come = frm.get("not_come")

    dto = SaveSingleAttendanceDTO(
        register_id=register_id,
        report_type=report_type,
        student_id=student_uid,
        register_date=register_date,
        register_notes=register_notes,
        register_extra=bool(register_extra),
        register_not_come=bool(register_not_come),
        current_user_id=current_user.id,
    )

    use_case = SaveSingleAttendanceUseCase(
        early_repo=SQLAlchemyEarlyRepository(),
        lunch_repo=SQLAlchemyLunchRepository(),
    )
    result = use_case.execute(dto)

    return make_response(jsonify(result), 200)
