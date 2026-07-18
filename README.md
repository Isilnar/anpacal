# ANPACAL

Web application for managing early morning childcare (madrugadores) and school cafeteria (comedor) services. Built for parent-teacher associations (ANPAs) to coordinate daily attendance, generate reports, and manage students, schools, and users.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Features](#features)
- [Test Credentials](#test-credentials)

## Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| Flask | 3.1 | Web framework |
| Werkzeug | 3.1 | WSGI toolkit (Flask dependency) |
| SQLAlchemy | 2.0 | ORM |
| Flask-SQLAlchemy | 3.1 | Flask-SQLAlchemy integration |
| SQLite | 3 | Database |
| Flask-Bcrypt | 1.0 | Password hashing |
| cryptography (Fernet) | 49.0 | PII field encryption |
| Flask-Talisman | 1.1 | Security headers (CSP) |
| Flask-WTF | 1.2 | CSRF protection |
| Flask-Login | 0.6 | Session management |
| Flask-Babel | 4.0 | Internationalization (gl/es/en) |
| Flask-Limiter | 4.1 | Rate limiting |
| Flask-Mail | 0.10 | Email delivery |
| openpyxl | 3.1 | Excel report generation |
| python-dotenv | 1.2 | Environment variable loading |
| pytz | 2026.2 | Timezone support |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| Bootstrap | 5.3 | UI framework |
| jQuery | 3.7 | DOM manipulation |
| FullCalendar | 6.1 | Interactive calendars |
| Moment.js | 2.30 | Date formatting (FullCalendar dependency) |
| Flatpickr | 4.6 | Date picker |
| Font Awesome | 6.7 | Icons |

### Tooling

| Tool | Version | Purpose |
|---|---|---|
| Ruff | 0.11 | Linter and formatter |
| pytest | 9.0 | Unit, integration, and E2E testing |
| pytest-cov | 7.1 | Coverage reporting |
| Playwright | 0.5+ | Browser-based E2E tests |
| Factory Boy | 3.3+ | Test data factories |
| pip-audit | 2.9 | Dependency vulnerability scanning (pre-commit hook) |
| pre-commit | - | Git hooks (ruff + pip-audit) |

> Note: `pip-audit` and `pre-commit` are installed globally or via `pip install pre-commit pip-audit`. They are not listed in requirements files.

## Installation

### Prerequisites

- Python 3.12+
- pip
- virtualenv (recommended)

### Steps

```bash
# Clone the repository
git clone <repo-url> anpacal
cd anpacal

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev/test dependencies (optional)
pip install -r requirements-dev.txt
pip install -r requirements-test.txt

# Copy environment template and fill in values
cp .env.example .env
```

### Environment Variables

Edit `.env` with the required values:

```dotenv
# Required — app will not start without these
SECRET_KEY=<generate-with-command-below>
FERNET_KEY=<generate-with-command-below>

# Optional — only if email delivery is needed
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_RESPONSE_ADDRESS=
```

Generate the required keys:

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(20))"

# FERNET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Instance Configuration

Application settings live in `instance/config.py` (git-ignored). Copy the example to get started:

```bash
cp instance/config.py.example instance/config.py
```

Key values to customize for your deployment:

| Variable | Description |
|---|---|
| `APP_TITLE` | Application name shown in browser tab and navbar |
| `COMPANY_NAME` | Organization name used in reports |
| `COMPANY_MAIL` | Contact email |
| `COPYRIGHT_TEXT` | Footer copyright text |
| `SCHOOL_YEAR_START` | Start date for the school year (update each September) |
| `CALENDAR_EDIT_CUTOFF_TIME` | `(hour, min, sec, µs)` — families can't edit the current day after this time (Europe/Madrid). Default: `(9, 15, 0, 0)` |
| `BABEL_DEFAULT_LOCALE` | Default language (`gl`, `es`, or `en`) |

## Running the Application

```bash
# Development server (HTTP on port 37666)
python run.py
```

The server starts on `http://0.0.0.0:37666`.

If TLS certificates are present at `certs/cert.pem` and `certs/key.pem`, the server will start with HTTPS automatically.

For production deployments with a WSGI server:

```bash
gunicorn flask_app:app
```

### Database Initialization

The database is created automatically on first startup (`db.create_all()`). Default roles, courses, and diet intolerances are seeded on the first request.

## Running Tests

```bash
# Unit + integration tests (excludes E2E)
pytest -m "not e2e"

# With coverage
pytest -m "not e2e" --cov=app --cov-report=html

# E2E tests (requires Playwright browsers installed)
playwright install chromium
pytest -m "e2e"
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Hooks run Ruff (lint + format) and pip-audit on every commit.

## Project Structure

```
anpacal/
├── app/                          # Application package
│   ├── adapters/                 # HTTP layer (Flask blueprints)
│   │   ├── decorators.py         # @admin_required
│   │   ├── intolerance_translations.py  # Allergen i18n helpers
│   │   ├── utils.py              # Shared adapter utilities
│   │   └── views/                # Route handlers (11 blueprint files)
│   ├── application/              # Use cases
│   │   ├── attendance/           # Attendance CRUD and reporting (17 use cases)
│   │   ├── holyday/              # Holiday management
│   │   ├── intolerance/          # Diet intolerance management
│   │   ├── menu/                 # Cafeteria menu link
│   │   ├── role/                 # Role queries
│   │   ├── school/               # School CRUD
│   │   ├── school_course/        # Course management
│   │   ├── student/              # Student CRUD
│   │   └── user/                 # User CRUD and auth
│   ├── domain/                   # Pure entities and repository interfaces
│   │   ├── attendance/           # EarlyAttendance, LunchAttendance
│   │   ├── student/              # Student, StudentWithAssociation
│   │   ├── user/                 # User, CryptoService, MailService
│   │   └── ...
│   ├── infrastructure/           # Repository implementations
│   │   ├── crypto.py             # Fernet encrypt/decrypt
│   │   ├── excel/                # Excel report generation
│   │   └── ...                   # SQLAlchemy ORM models and repos
│   ├── static/                   # CSS, JS, images, fonts
│   ├── templates/                # Jinja2 templates (31 files)
│   └── translations/             # i18n catalogs (gl, es, en)
├── instance/
│   └── config.py                 # Deployment-specific configuration
├── scripts/                      # Migration utilities
│   ├── migrate_fernet.py         # Encrypt PII fields
│   └── migrate_to_bcrypt.py      # Hash passwords with bcrypt
├── tests/
│   ├── e2e/                      # Playwright browser tests
│   ├── factories/                # Factory Boy test data factories (19 files)
│   ├── integration/              # Repository tests (real DB)
│   └── unit/                     # Domain and use case tests
├── run.py                        # Dev server entry point
├── flask_app.py                  # WSGI entry point
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Dev dependencies (pytest, coverage)
├── requirements-test.txt         # Test dependencies (Playwright, Factory Boy)
└── pyproject.toml                # Ruff, pytest, coverage config
```

### Architecture

The project follows **Clean Architecture** (Hexagonal):

```
adapters  →  application  →  domain
   │              │              │
Flask routes   Use cases    Pure entities
Blueprints     Orchestration  Repository interfaces (ABC)
                              No framework imports

infrastructure (implements domain interfaces)
   │
SQLAlchemy ORMs, Fernet crypto, Excel, Mail
```

The dependency rule is strictly enforced: inner layers know nothing about outer layers.

## Features

### User Roles

| Role | Access |
|---|---|
| **admin** | Full management: users, students, schools, holidays, reports, register editing |
| **family** | Family calendar: request early-care and lunch services per day/range |
| **earlycare** | Early-care calendar and daily reports |
| **lunchcare** | Lunch-care calendar and summary reports |

### Core Functionality

- **Attendance calendars** — Interactive FullCalendar views where families select early-care and/or lunch for each day. Care workers see their own view with student lists.
- **Multi-day requests** — Families can set attendance for a date range in one action.
- **Student management** — CRUD with dietary intolerance tracking (16 pre-configured allergens).
- **School management** — Multiple schools supported with course assignments.
- **Holiday management** — Define non-school days; attendance cannot be registered on holidays.
- **Excel reports** — Export attendance data as `.xlsx` files filtered by date range, student, service type.
- **Register editing** — Admin can manually add, modify, or delete individual attendance records.
- **Menu link** — Admin sets an external URL to the current cafeteria menu, visible to all users.
- **Internationalization** — Full UI translation in Galician, Spanish, and English. Language switch in navbar.
- **PWA support** — Optional Progressive Web App mode with install prompt, offline page, and push notifications (controlled by `IS_PWA` config flag).
- **Security** — Bcrypt password hashing, Fernet PII encryption, CSP headers, CSRF protection, rate limiting on login.

## Test Credentials

The application seeds default roles on first startup but does **not** create a default admin user. For local development, the E2E test suite creates the following users in an in-memory database:

| User | Password | Role |
|---|---|---|
| `e2e_admin` | `e2e_pass` | admin |
| `e2e_family_user` | `family_pass` | family |
| `e2e_earlycare_user` | `earlycare_pass` | earlycare |
| `e2e_lunchcare_user` | `lunchcare_pass` | lunchcare |

To create an admin user in the production database, use the Flask shell:

```bash
python -c "
from app import create_app, db
from app.infrastructure.user.orm import UserORM, UserRoleAssociation
from app.infrastructure.role.orm import RoleORM
from flask_bcrypt import generate_password_hash

app = create_app()
with app.app_context():
    role = RoleORM.query.filter_by(name='admin').first()
    user = UserORM(
        username='admin',
        password=generate_password_hash('admin123').decode('utf-8'),
        name='Admin',
        surname='User',
        status=1
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(UserRoleAssociation(user_id=user.id, role_id=role.id))
    db.session.commit()
    print('Admin user created: admin / admin123')
"
```
