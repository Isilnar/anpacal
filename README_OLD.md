# anpacal

Aplicación de xestión de madrugadores e comedor escolar para ANPAs. Permite rexistrar asistencias, xestionar alumnado e cursos, controlar intolerancias alimentarias e xerar informes.

Desenvolvida con Flask 3 + SQLAlchemy 2, autenticación con bcrypt, cifrado Fernet para datos PII, soporte i18n (es/gl/en/ca/eu) e WebSockets en tempo real.

---

## Requisitos

- Python 3.14+
- SQLite (incluído en Python — non require instalación)

---

## Instalación

```bash
git clone https://github.com/tu-usuario/anpacal.git
cd anpacal

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Configuración

### 1. Variables de entorno

```bash
cp .env.example .env
```

Edita `.env` e completa os valores:

```dotenv
SECRET_KEY=<xerado no paso seguinte>
FERNET_KEY=<xerado no paso seguinte>
```

**Xerar `SECRET_KEY`:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(20))"
```

**Xerar `FERNET_KEY`:**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Configuración da instancia

Crea o arquivo `instance/config.py` (non se commitea — contén valores locais):

```python
import os

DEBUG = True
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
USE_BCRYPT = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///../database_bcrypt.db'

SECRET_KEY = os.environ.get('SECRET_KEY', '')
FERNET_KEY = os.environ.get('FERNET_KEY', '')

LANGUAGES = ['es', 'en', 'gl', 'ca', 'eu']
APP_TITLE = "Mi ANPA"
APP_DESC = "Aplicación de xestión de madrugadores e comedor"

SERVER_HOST_NO_CERTS = "0.0.0.0"
SERVER_PORT_NO_CERTS = 37666
SERVER_HOST_WITH_CERTS = "0.0.0.0"
SERVER_PORT_WITH_CERTS = 37666

# Mail (opcional — só se precisas envío de contrasinais por correo)
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_RESPONSE_ADDRESS = os.environ.get('MAIL_RESPONSE_ADDRESS', '')
```

### Variables obrigatorias vs opcionais

| Variable | Obrigatoria | Descripción |
|---|---|---|
| `SECRET_KEY` | Si | Firmado de sesiones Flask |
| `FERNET_KEY` | Si | Cifrado de datos PII (DNI, email, teléfono) |
| `MAIL_SERVER` | Non | Servidor SMTP para envío de contrasinais |
| `MAIL_PORT` | Non | Porto SMTP (default: 587) |
| `MAIL_USE_TLS` | Non | Usar TLS (default: True) |
| `MAIL_USERNAME` | Non | Usuario SMTP |
| `MAIL_PASSWORD` | Non | Contrasinal SMTP |
| `MAIL_RESPONSE_ADDRESS` | Non | Dirección de resposta nos correos |

---

## Base de datos

Non se require ningún paso manual. Ao arrancar a aplicación:

1. `db.create_all()` crea todas as táboas automáticamente.
2. `setup()` execútase en cada petición (idempotente) e sembra os datos iniciais:
   - **Roles**: admin, family, earlycare, lunchcare
   - **Cursos**: 4º EI → 6º EP (9 cursos)
   - **Intolerancias**: 16 alérgenos por defecto (glute, lácteos, ovos…)

### Scripts de migración (só se migras dende versión antiga)

```bash
# Migrar contrasinais planos a bcrypt
python scripts/migrate_to_bcrypt.py

# Cifrar campos PII con Fernet (DNI, email, teléfono)
python scripts/migrate_fernet.py
```

> Estes scripts só son necesarios se tes unha base de datos anterior sen bcrypt nin Fernet. Unha instalación nova non os precisa.

---

## Arrancar o servidor

```bash
python run.py
```

A aplicación arranca en `http://0.0.0.0:37666`.

**Con certificados TLS** (opcional): coloca `certs/cert.pem` e `certs/key.pem` na raíz do proxecto. `run.py` detectaos automaticamente e arranca con HTTPS.

---

## Tests

```bash
pip install -r requirements-test.txt

# Tests unitarios e de integración
python -m pytest tests/ --ignore=tests/e2e

# Tests end-to-end (Playwright)
python -m playwright install chromium
python -m pytest tests/e2e/
```

---

## Arquitectura

O proxecto segue Clean Architecture con 4 capas:

```
app/
├── domain/          # Entidades e regras de negocio puras
│   ├── user/        # Usuario, roles
│   ├── student/     # Alumno, intolerancias
│   ├── attendance/  # Rexistros de asistencia
│   ├── school/      # Centro, cursos
│   ├── menu/        # Menú do comedor
│   └── holyday/     # Festivos
├── application/     # Casos de uso (un directorio por entidade)
├── infrastructure/  # Repositorios SQLAlchemy, adaptadores externos
├── adapters/        # Blueprints Flask, formularios, vistas HTTP
└── models/          # Modelos ORM (SQLAlchemy)
```

As dependencias apuntan sempre cara ao interior: `adapters → application → domain`. O dominio non coñece Flask nin SQLAlchemy.
