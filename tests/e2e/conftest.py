import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser_context(live_server_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        browser.close()


@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture
def fresh_page(browser_context):
    """Página en un browser context limpio (sin cookies de sesión).

    Crea un nuevo contexto aislado dentro del mismo browser para garantizar
    que no hay cookies de sesión activas, incluso si otros tests del módulo
    ya iniciaron sesión en el browser_context compartido.
    """
    # Obtener el browser desde el contexto existente
    browser = browser_context.browser
    # Crear un contexto nuevo y aislado (sin cookies)
    isolated_context = browser.new_context()
    isolated_page = isolated_context.new_page()
    yield isolated_page
    isolated_context.close()


@pytest.fixture(scope="session")
def admin_seed(app):
    """Crea el usuario admin e2e_admin en la DB de test (scope=session).

    Depende del fixture `app` (scope=session) de tests/conftest.py,
    que ya hizo db.create_all().  El seed ocurre una sola vez por sesión
    de pytest, antes de que los tests de login corran.

    Returns:
        dict con username y password en claro para usar en page.fill().
    """
    from app import bcrypt, db
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation

    with app.app_context():
        # 1. Role admin (idempotente — no duplicar si ya existe)
        role = Role.query.filter_by(name="admin").first()
        if role is None:
            role = Role(name="admin", description="Administrador")
            db.session.add(role)
            db.session.flush()  # obtener role.id sin commit completo

        # 2. User e2e_admin (idempotente)
        user = User.query.filter_by(username="e2e_admin").first()
        if user is None:
            user = User(
                username="e2e_admin",
                password=bcrypt.generate_password_hash("e2e_pass").decode("utf-8"),
                name="E2E",
                surname="Admin",
                status=1,
                ws_token="e2e-token-unique-seed",
            )
            db.session.add(user)
            db.session.flush()  # obtener user.id

        # 3. Asociación user ↔ role (idempotente — UserRoleAssociation es PK compuesta)
        assoc = UserRoleAssociation.query.filter_by(user_id=user.id, role_id=role.id).first()
        if assoc is None:
            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)

        db.session.commit()

    return {"username": "e2e_admin", "password": "e2e_pass"}


@pytest.fixture(scope="session")
def cuidadora_seed(app):
    """Crea usuarios coidadora (earlycare y lunchcare) con una escuela en la DB de test.

    Crea:
      - School "E2E Cuidadora School"
      - Role 'earlycare' + User 'e2e_earlycare_user' + UserSchoolAssociation
      - Role 'lunchcare' + User 'e2e_lunchcare_user' + UserSchoolAssociation

    El seed es idempotente: comprueba existencia antes de insertar.

    Returns:
        dict con credenciales de earlycare y lunchcare, y school_id.
    """
    from app import bcrypt, db
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.school.orm import SchoolORM as School
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation, UserSchoolAssociation

    with app.app_context():
        # 1. Escuela (idempotente)
        school = School.query.filter_by(name="E2E Cuidadora School").first()
        if school is None:
            school = School(
                name="E2E Cuidadora School",
                address="Rúa Cuidadora, 1",
                phone="981000200",
                email="cuidadora@e2e.com",
                status=1,
            )
            db.session.add(school)
            db.session.flush()

        # 2. Role earlycare (idempotente)
        role_early = Role.query.filter_by(name="earlycare").first()
        if role_early is None:
            role_early = Role(name="earlycare", description="Coidadora madrugadores")
            db.session.add(role_early)
            db.session.flush()

        # 3. User e2e_earlycare_user (idempotente)
        user_early = User.query.filter_by(username="e2e_earlycare_user").first()
        if user_early is None:
            user_early = User(
                username="e2e_earlycare_user",
                password=bcrypt.generate_password_hash("earlycare_pass").decode("utf-8"),
                name="E2E",
                surname="Earlycare",
                status=1,
                ws_token="e2e-token-earlycare-seed",
            )
            db.session.add(user_early)
            db.session.flush()

        # 4. UserRoleAssociation earlycare (idempotente)
        assoc_role_early = UserRoleAssociation.query.filter_by(user_id=user_early.id, role_id=role_early.id).first()
        if assoc_role_early is None:
            assoc_role_early = UserRoleAssociation(user_id=user_early.id, role_id=role_early.id)
            db.session.add(assoc_role_early)

        # 5. UserSchoolAssociation earlycare ↔ school (idempotente)
        assoc_school_early = UserSchoolAssociation.query.filter_by(user_id=user_early.id, school_id=school.id).first()
        if assoc_school_early is None:
            assoc_school_early = UserSchoolAssociation(user_id=user_early.id, school_id=school.id)
            db.session.add(assoc_school_early)

        # 6. Role lunchcare (idempotente)
        role_lunch = Role.query.filter_by(name="lunchcare").first()
        if role_lunch is None:
            role_lunch = Role(name="lunchcare", description="Coidadora comedor")
            db.session.add(role_lunch)
            db.session.flush()

        # 7. User e2e_lunchcare_user (idempotente)
        user_lunch = User.query.filter_by(username="e2e_lunchcare_user").first()
        if user_lunch is None:
            user_lunch = User(
                username="e2e_lunchcare_user",
                password=bcrypt.generate_password_hash("lunchcare_pass").decode("utf-8"),
                name="E2E",
                surname="Lunchcare",
                status=1,
                ws_token="e2e-token-lunchcare-seed",
            )
            db.session.add(user_lunch)
            db.session.flush()

        # 8. UserRoleAssociation lunchcare (idempotente)
        assoc_role_lunch = UserRoleAssociation.query.filter_by(user_id=user_lunch.id, role_id=role_lunch.id).first()
        if assoc_role_lunch is None:
            assoc_role_lunch = UserRoleAssociation(user_id=user_lunch.id, role_id=role_lunch.id)
            db.session.add(assoc_role_lunch)

        # 9. UserSchoolAssociation lunchcare ↔ school (idempotente)
        assoc_school_lunch = UserSchoolAssociation.query.filter_by(user_id=user_lunch.id, school_id=school.id).first()
        if assoc_school_lunch is None:
            assoc_school_lunch = UserSchoolAssociation(user_id=user_lunch.id, school_id=school.id)
            db.session.add(assoc_school_lunch)

        # Capture ID before commit to avoid expire-on-refresh issues under StaticPool.
        school_id = school.id

        db.session.commit()

    return {
        "earlycare": {"username": "e2e_earlycare_user", "password": "earlycare_pass"},
        "lunchcare": {"username": "e2e_lunchcare_user", "password": "lunchcare_pass"},
        "school_id": school_id,
    }


@pytest.fixture(scope="session")
def family_seed(app):
    """Crea un usuario de familia con un alumno vinculado en la DB de test.

    Crea:
      - School "E2E Family School"
      - Role 'family'
      - User 'e2e_family_user'
      - Student 'E2E FamilyStudent' vinculado a la escuela
      - UserStudentAssociation usuario ↔ alumno

    El seed es idempotente: comprueba existencia antes de insertar.

    Returns:
        dict con credenciales de family, school_id y student_id.
    """
    from app import bcrypt, db
    from app.infrastructure.role.orm import RoleORM as Role
    from app.infrastructure.school.orm import SchoolORM as School
    from app.infrastructure.student.orm import StudentORM as Student
    from app.infrastructure.user.orm import UserORM as User
    from app.infrastructure.user.orm import UserRoleAssociation, UserStudentAssociation

    with app.app_context():
        # 1. Escuela (idempotente)
        school = School.query.filter_by(name="E2E Family School").first()
        if school is None:
            school = School(
                name="E2E Family School",
                address="Rúa Familia, 2",
                phone="981000300",
                email="family@e2e.com",
                status=1,
            )
            db.session.add(school)
            db.session.flush()

        # 2. Alumno vinculado a la escuela (idempotente)
        student = Student.query.filter_by(name="E2EFamilyStudent").first()
        if student is None:
            student = Student(
                name="E2EFamilyStudent",
                surname="E2ESurname",
                school_id=school.id,
                status=1,
            )
            db.session.add(student)
            db.session.flush()

        # 3. Role family (idempotente)
        role_family = Role.query.filter_by(name="family").first()
        if role_family is None:
            role_family = Role(name="family", description="Familia")
            db.session.add(role_family)
            db.session.flush()

        # 4. User e2e_family_user (idempotente)
        user_family = User.query.filter_by(username="e2e_family_user").first()
        if user_family is None:
            user_family = User(
                username="e2e_family_user",
                password=bcrypt.generate_password_hash("family_pass").decode("utf-8"),
                name="E2E",
                surname="Family",
                status=1,
                ws_token="e2e-token-family-seed",
            )
            db.session.add(user_family)
            db.session.flush()

        # 5. UserRoleAssociation family (idempotente)
        assoc_role = UserRoleAssociation.query.filter_by(user_id=user_family.id, role_id=role_family.id).first()
        if assoc_role is None:
            assoc_role = UserRoleAssociation(user_id=user_family.id, role_id=role_family.id)
            db.session.add(assoc_role)

        # 6. UserStudentAssociation usuario ↔ alumno (idempotente)
        assoc_student = UserStudentAssociation.query.filter_by(user_id=user_family.id, student_id=student.id).first()
        if assoc_student is None:
            assoc_student = UserStudentAssociation(user_id=user_family.id, student_id=student.id)
            db.session.add(assoc_student)

        # Save IDs BEFORE commit — expire_on_commit expires all managed objects.
        school_id = school.id
        student_id = student.id

        db.session.commit()

    return {
        "username": "e2e_family_user",
        "password": "family_pass",
        "school_id": school_id,
        "student_id": student_id,
    }
