# student_routes.py — Adapter: rutas CRUD de estudiante delegando a use cases.
#
# Blueprint 'student_bp' con prefijo '/management/students'.
# Convive con el blueprint 'management_station' en management.py (Strangler Fig).

from flask import Blueprint, flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_babel import _
from flask_login import login_required

from app.adapters.decorators import admin_required
from app.adapters.utils import get_current_schools, get_selected_intolerances
from app.application.student.create import CreateStudentUseCase, DuplicateStudentError
from app.application.student.delete import DeleteStudentUseCase
from app.application.student.dtos import StudentCreateDTO, StudentEditDTO
from app.application.student.edit import EditStudentUseCase
from app.application.student.get import GetStudentUseCase, StudentNotFoundError
from app.application.student.get_all_with_association import GetAllWithAssociationUseCase
from app.application.student.list_students import ListStudentsUseCase
from app.infrastructure.school_course.repository import SQLAlchemySchoolCourseRepository
from app.infrastructure.student.repository import SQLAlchemyStudentRepository
from app.infrastructure.user.crypto_service import FernetCryptoService

student_bp = Blueprint("student_bp", __name__, url_prefix="/management/students")


def _make_repo():
    return SQLAlchemyStudentRepository()


def _make_crypto():
    return FernetCryptoService()


# ---------------------------------------------------------------------------
# GET / — listar estudiantes activos
# ---------------------------------------------------------------------------
@student_bp.route("/")
@login_required
@admin_required
def list_students():
    repo = _make_repo()
    students = ListStudentsUseCase(repo).execute()
    intolerances_list = get_selected_intolerances()
    schools_list = get_current_schools()
    school_courses = SQLAlchemySchoolCourseRepository().list_all()
    return render_template(
        "station/management/edit_student.html",
        students_list=students,
        intolerances_list=intolerances_list,
        schools_list=schools_list,
        school_courses=school_courses,
        menu_link="",
    )


def _build_create_dto(frm) -> StudentCreateDTO:
    intolerance_ids = [int(i) for i in frm.get("selectedIntolerancesIds", "").split(",") if i]
    return StudentCreateDTO(
        name=frm.get("studentName", ""),
        surname=frm.get("studentSurname", ""),
        school_id=int(frm.get("selectedSchool", 0) or 0),
        classroom=frm.get("studentClassroom", ""),
        number_id=frm.get("numberID", ""),
        phone=frm.get("studentPhone", ""),
        email=frm.get("studentMail", ""),
        address=frm.get("studentAddress", ""),
        allergies=frm.get("studentAllergies", ""),
        childish=frm.get("studentChildish", ""),
        brother_number=int(frm.get("studentBrother", 0) or 0),
        student_number=frm.get("studentNumber", ""),
        intolerance_ids=intolerance_ids,
    )


# ---------------------------------------------------------------------------
# POST / — crear estudiante
# ---------------------------------------------------------------------------
@student_bp.route("/", methods=["POST"])
@login_required
@admin_required
def create_student():
    dto = _build_create_dto(request.form)
    use_case = CreateStudentUseCase(_make_repo(), _make_crypto())
    try:
        use_case.execute(dto)
        flash(_("Rexistrouse un novo alumno"))
    except DuplicateStudentError:
        flash(_("Xa existe un alumno co mesmo DNI neste colexio"))
    return redirect(url_for("student_bp.list_students"))


# ---------------------------------------------------------------------------
# GET /<student_id> — obtener estudiante (JSON)
# ---------------------------------------------------------------------------
@student_bp.route("/<int:student_id>")
@login_required
@admin_required
def get_student(student_id: int):
    try:
        student = GetStudentUseCase(_make_repo()).execute(student_id)
        return make_response(jsonify(vars(student)), 200)
    except StudentNotFoundError:
        return make_response(jsonify({"error": "not found"}), 404)


# ---------------------------------------------------------------------------
# POST /<student_id> — editar estudiante
# ---------------------------------------------------------------------------
@student_bp.route("/<int:student_id>", methods=["POST"])
@login_required
@admin_required
def edit_student(student_id: int):
    frm = request.form
    intolerance_ids = [int(i) for i in frm.get("selectedIntolerancesIds", "").split(",") if i]
    dto = StudentEditDTO(
        student_id=student_id,
        name=frm.get("studentName", ""),
        surname=frm.get("studentSurname", ""),
        school_id=int(frm.get("selectedSchool", 0) or 0),
        classroom=frm.get("studentClassroom", ""),
        number_id=frm.get("numberID", ""),
        phone=frm.get("studentPhone", ""),
        email=frm.get("studentMail", ""),
        address=frm.get("studentAddress", ""),
        allergies=frm.get("studentAllergies", ""),
        childish=frm.get("studentChildish", ""),
        brother_number=int(frm.get("studentBrother", 0) or 0),
        intolerance_ids=intolerance_ids,
    )
    try:
        EditStudentUseCase(_make_repo(), _make_crypto()).execute(dto)
        flash(_("Modificáronse os parámetros do alumno"))
    except Exception:
        flash(_("Alumno non atopado"))
    return redirect(url_for("student_bp.list_students"))


# ---------------------------------------------------------------------------
# POST /<student_id>/delete — soft-delete estudiante
# ---------------------------------------------------------------------------
@student_bp.route("/<int:student_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_student(student_id: int):
    try:
        DeleteStudentUseCase(_make_repo()).execute(student_id)
        flash(_("Eliminouse o alumno seleccionado"))
    except Exception:
        flash(_("Alumno non atopado"))
    return redirect(url_for("student_bp.list_students"))


# ---------------------------------------------------------------------------
# POST /all — obtener todos los estudiantes con flag de asociación (JSON)
# ---------------------------------------------------------------------------
@student_bp.route("/all", methods=["POST"])
@login_required
@admin_required
def get_all_students():
    user_id = request.json.get("user") if request.is_json else None
    use_case = GetAllWithAssociationUseCase(_make_repo())
    results = use_case.execute(user_id=user_id)
    students = [{**vars(r.student), "associated": 1 if r.associated else 0} for r in results]
    return make_response(jsonify(students), 200)
