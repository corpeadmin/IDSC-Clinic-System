# IDSC Clinic System

IDSC Clinic System is a web-based system designed to streamline clinic operations by reducing manual work, organizing clinic processes, and making it easier for clinic workers to efficiently manage their daily tasks.

---

## 1. Project Overview

The **IDSC Clinic System** provides a centralized digital platform for managing student health records, consultations, physical measurements, and clinic visit histories. Student identifiers are supplied by an external Registrar system.

### Core Objectives
* **Streamline Clinic Operations**: Eliminates paper-based clinic record keeping and manual logs.
* **Organize Student Medical Data**: Stores student identifiers alongside chronological health records, vital stats, allergies, and consultation notes.
* **Efficient Lookup & History**: Enables clinic staff to search students by student ID and inspect visit histories instantly.
* **External System Integration**: Exposes a dedicated view-only Health Record API for the Student Portal System and a full Health Status CRUD API for the Faculty System.

### Component Responsibilities
* **Backend (`backend/`)**: Built with Python and Django 6.1, exposing a RESTful JSON API using Django REST Framework (DRF). Handles business logic, input validation, relationship integrity, and database operations via Django ORM.
* **REST API (`/api/`)**: Provides CRUD endpoints for Students, Health Records, and Consultations, plus nested relationship endpoints for querying and creating records tied to specific students. Also provides a view-only Health Record API for the Student Portal System and a full Health Status CRUD API for the Faculty System.
* **Session Authentication (`/api/auth/`)**: Provides `csrf`, `login`, `logout`, and `me` endpoints backed by Django sessions.
* **PostgreSQL (`clinic_db`)**: The relational database management system running in a Docker container (`clinic-postgres`). Enforces table constraints, foreign keys, database indexes, and externally supplied primary keys.
* **Django Admin (`/admin/`)**: Built-in administrative back-office portal with tabular inlines, multi-field search, and filtering for authorized clinic personnel. **This is currently the only working user interface in the project.**
* **Frontend (`frontend/`)**: React 19 + Vite project. ⚠ **The UI is not implemented** — `frontend/src/App.jsx` is the unmodified Vite starter template. See [Project Status](#2a-project-status).

---

## 1a. Documentation Map

Detailed technical documentation lives in [`docs/`](docs/README.md):

| Document | Contents |
| :--- | :--- |
| [`docs/architecture.md`](docs/architecture.md) | System context, backend layers, endpoint inventory, request lifecycle, screen-to-endpoint map, known defects |
| [`docs/data-model.md`](docs/data-model.md) | Entities, fields, ER diagram, index strategy, migration history, model-to-API alignment |
| [`docs/integration.md`](docs/integration.md) | External systems, shared IDs and ports, error contract, agreements log |
| [`docs/design-system.md`](docs/design-system.md) | Actual current UI state — records that no design system, screens, or screenshots exist |
| [`docs/decisions/`](docs/decisions/) | Architecture decision records |

---

## 2. Technology Stack

All technology versions match the project's actual configuration:

### Backend
* **Python**: `3.10+` (development environment uses `3.14`)
* **Django**: `6.1` (`>=6.1,<6.2`)
* **Django REST Framework (DRF)**: `3.18.0` (`>=3.18.0,<3.19`)
* **PostgreSQL Driver (`psycopg`)**: `3.3.4` (using `psycopg[binary]`)
* **CORS Middleware (`django-cors-headers`)**: `4.9.0`
* **OpenAPI Schema (`drf-spectacular`)**: `0.30.0`
* **Environment Configuration (`python-dotenv`)**: `1.2.3`

### Database
* **PostgreSQL**: `16-alpine` (hosted via Docker container `clinic-postgres`)

### Frontend
* **React**: `19.2.8`
* **React DOM**: `19.2.8`
* **Vite**: `8.2.0`
* **ESLint**: `10.8.0`
* **Node.js / npm**: Node 18+ runtime environment

> Pinning note: `backend/requirements.txt` uses compatible-release ranges (`>=x,<y`), not exact
> pins. The versions above are those recorded in the project documentation and match the ranges.

---

## 2a. Project Status

Current state, so this README is not read as a description of finished software.

### Working
* Four models with foreign keys, indexes, and `ON DELETE CASCADE`
* Five viewsets under `/api/` — full CRUD, a read-only Student Portal surface, and nested per-student routes
* Migration chain `0001` → `0005`, including a data migration that split consultations out of health records
* Custom DRF exception handler producing a uniform `{success, status_code, errors}` envelope
* Session authentication endpoints under `/api/auth/`
* Django Admin with inlines for all four models — the only working UI
* OpenAPI schema, Swagger UI, and ReDoc at `/api/schema/`
* **54 automated tests, all passing**

### Not built
* **Frontend UI** — the Vite starter template is unmodified; no clinic screen, API call, router, or state management
* **Frontend-to-backend wiring** — `vite.config.js` defines no dev-server proxy and no API base URL
* **Screenshots and design system** — no screens exist to capture; no design system or Figma file is referenced in the repository
* **Registrar integration** — student IDs are caller-supplied; there is no inbound endpoint, webhook, or import job
* **API authentication enforcement** — `AllowAny` is configured globally

### Known defects
Documented in [`docs/architecture.md §6.3`](docs/architecture.md#63-known-defects-found-while-verifying-this-document). Most significant: `?search=` on `/api/health-records/` raises `FieldError` because it filters on a reverse relation belonging to `Student`, not `HealthRecord` (`views.py:283`). No test covers it, so the suite still passes.

---

## 3. System Architecture

The application follows a clean layered architecture:

```text
┌───────────────────────────────────────────────────────────┐
│                 Frontend (React 19 + Vite)                │
│                 http://localhost:5173                     │
│        ⚠ Starter template only — not implemented          │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP / JSON (CORS Enabled)
                              ▼
┌───────────────────────────────────────────────────────────┐
│             Django REST API (Views & ViewSets)            │
│   StudentViewSet  │  HealthRecordViewSet                  │
│   ConsultationViewSet │ StudentPortalHealthRecordViewSet   │
│   HealthStatusViewSet                                    │
└─────────────────────────────┬─────────────────────────────┘
                              │ Validated Data / Serializers
                              ▼
┌───────────────────────────────────────────────────────────┐
│               Django ORM (Models & QuerySets)             │
│        Student │ HealthRecord │ Consultation │ HealthStatus│
└─────────────────────────────┬─────────────────────────────┘
                              │ PostgreSQL Protocol (psycopg 3)
                              ▼
┌───────────────────────────────────────────────────────────┐
│        PostgreSQL Database (Docker: clinic-postgres)      │
│                     Database: clinic_db                   │
│ students │ health_records │ consultations │ health_statuses│
└───────────────────────────────────────────────────────────┘
```

### Layer Responsibilities
1. **Frontend**: Intended to render the UI and call the API. Not implemented — currently the Vite starter template.
2. **Django REST API**: Authenticates requests, parses JSON payloads, runs serializer validations, handles exceptions gracefully, and returns HTTP status codes. Serves the clinic UI, the Student Portal System (view-only health records), and the Faculty System (health status CRUD).
3. **Django ORM**: Translates Python model queries into parameterized SQL statements, safeguarding against SQL injection and maintaining relational constraints.
4. **PostgreSQL**: Persists tables, stores externally supplied primary keys (`student_id`), enforces foreign-key referential integrity (`ON DELETE CASCADE`), and optimizes search via B-tree indexes.

---

## 4. Project Structure

```text
IDSC Clinic System/
├── README.md                          # Main technical & developer documentation
├── SETUP.md                           # Step-by-step installation, setup & troubleshooting guide
├── API.md                             # Generated API reference
├── openapi.json / openapi.yaml        # OpenAPI 3 schema (drf-spectacular, generated 2026-09-22)
├── main.py                            # Unrelated PyCharm scratch script (prints "Hi, PyCharm")
├── docs/                              # Detailed technical documentation
│   ├── README.md                      # Documentation index and project status
│   ├── architecture.md                # Context, layers, endpoints, known defects
│   ├── data-model.md                  # Entities, fields, ER diagram, migrations
│   ├── integration.md                 # External systems, shared IDs/ports, agreements log
│   ├── design-system.md               # Actual UI state (no design system exists)
│   └── decisions/                     # Architecture decision records
│       ├── README.md
│       ├── 0001-backend-framework-django-drf.md
│       ├── 0002-split-consultations-from-health-records.md
│       └── 0003-externally-supplied-student-id.md
├── backend/                           # Django backend application root
│   ├── manage.py                      # Django CLI management script
│   ├── requirements.txt               # Backend Python dependencies
│   ├── .env                           # Local environment credentials (not committed)
│   ├── .env.example                   # Environment variable template
│   ├── config/                        # Django project configuration module
│   │   ├── __init__.py
│   │   ├── asgi.py                    # ASGI configuration for async deployment
│   │   ├── settings.py                # Database, DRF, CORS, and app settings
│   │   ├── urls.py                    # Root URL routing and API endpoint registration
│   │   └── wsgi.py                    # WSGI configuration for production deployment
│   ├── authentication/                # Session authentication app
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py                  # (no custom models; uses django.contrib.auth)
│   │   ├── urls.py                    # csrf / login / logout / me routes
│   │   └── views.py                   # Session auth views
│   └── clinic/                        # Main Clinic Django application
│       ├── __init__.py
│       ├── admin.py                   # Django Admin registrations & inlines
│       ├── apps.py                    # App configuration (ClinicConfig)
│       ├── exceptions.py              # Custom API exception handler
│       ├── models.py                  # Student, HealthRecord, Consultation, HealthStatus models
│       ├── serializers.py             # DRF serializers & field validation logic
│       ├── tests.py                   # 54 automated unit & integration tests
│       ├── urls.py                    # Clinic API router registrations
│       ├── views.py                   # All five viewsets
│       └── migrations/                # Database migration history
│           ├── 0001_initial.py                    # Initial students + health_records tables
│           ├── 0002_alter_student_student_id.py   # Auto-increment student_id migration
│           ├── 0003_remove_student_idx_student_name_and_more.py  # Simplified student schema
│           ├── 0004_healthstatus.py              # Health Status table creation
│           └── 0005_consultation.py               # Consultations table; moves visit/consultation out of health_records
├── frontend/                          # Vite + React project (starter template, UI NOT implemented)
│   ├── index.html                     # HTML entry template
│   ├── package.json                   # Frontend dependencies and npm scripts
│   ├── vite.config.js                 # Vite config — React plugin only, no API proxy
│   ├── eslint.config.js               # ESLint configuration
│   ├── README.md                      # Vite starter README
│   └── src/                           # Frontend source code
│       ├── main.jsx                   # React application root mount point
│       ├── App.jsx                    # Vite starter landing page (not clinic UI)
│       ├── App.css                    # Template stylesheet
│       ├── index.css                  # Template stylesheet + CSS custom properties
│       └── assets/                    # Template images and SVG logos
└── gen/                               # ⚠ STALE generated OpenAPI Python client (7.7.0)
    └── openapi_client/                # Predates the Consultation split — see docs/data-model.md §9
```

---

## 5. Database Architecture

The development database runs in a Docker container named `clinic-postgres`:

```text
Docker Desktop
└── clinic-postgres (Container: PostgreSQL 16-alpine)
    └── PostgreSQL Server (Port 5432)
└── clinic_db (Database)
        ├── Django Framework Tables (auth, sessions, admin, contenttypes)
        ├── students (Student entity table)
        ├── health_records (HealthRecord entity table)
        ├── consultations (Consultation entity table)
        └── health_statuses (HealthStatus entity table)
```

* **Server & Host**: `localhost:5432`
* **Database Name**: `clinic_db`
* **Default User / Password**: `postgres` / `postgres`
* **Schema Management**: Managed exclusively by Django migrations (`python manage.py migrate`). **Developers should never manually create tables with raw SQL.**

---

## 6. Django Built-in Tables

Applying migrations automatically generates the standard Django framework tables:

* `auth_user` — User accounts for administrative access
* `auth_group` — User permission groups
* `auth_permission` — Individual model/action permissions
* `auth_group_permissions` — Group-to-permission mappings
* `auth_user_groups` — User-to-group mappings
* `auth_user_user_permissions` — User-to-permission mappings
* `django_admin_log` — Audit logs of Django admin actions
* `django_content_type` — Content type definitions for Django models
* `django_migrations` — Applied migration history ledger
* `django_session` — HTTP session store

---

## 7. Student Model

Defined in [`backend/clinic/models.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/models.py):

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | `BigIntegerField` | `primary_key=True` | Externally supplied unique student identifier. Must be provided on creation. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Record last-updated timestamp. |

### Database Metadata
* **Table Name**: `students`
* **Default Ordering**: `['student_id']`
* **Indexes**: None

> [!IMPORTANT]
> `student_id` is an **externally supplied primary key**. It must be provided when creating a student and must not be auto-generated by the database.

---

## 8. Health Record Model

Defined in [`backend/clinic/models.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/models.py):

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `health_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing unique health record ID. |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='health_records'` | Relational foreign key referencing `students.student_id`. |
| `allergies` | `TextField` | `blank=True, default=''` | Known medical, food, or environmental allergies. |
| `blood_type` | `CharField(max_length=10)` | `choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown']`, `blank=True, default=''` | Student blood group. |
| `medical_history` | `TextField` | `blank=True, default=''` | Chronic illnesses or past medical history. |
| `medication` | `TextField` | `blank=True, default=''` | Current medications and prescriptions. |
| `weight` | `DecimalField(5, 2)` | `null=True, blank=True`, `min=0.0, max=500.0` | Weight in kilograms (kg). |
| `height` | `DecimalField(5, 2)` | `null=True, blank=True`, `min=0.0, max=300.0` | Height in centimeters (cm). |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Record last-updated timestamp. |

### Database Metadata
* **Table Name**: `health_records`
* **Default Ordering**: `['-health_id']`
* **Indexes**: `idx_hr_student_id` on `(student_id, -health_id)`

> [!IMPORTANT]
> `HealthRecord` **no longer has `visit` or `consultation` columns.** Both were moved to the
> `Consultation` model by migration `0005_consultation.py`. See [ADR-0002](docs/decisions/0002-split-consultations-from-health-records.md).
> Any client, mock, or document still sending or expecting `visit` / `consultation` on a health
> record is out of date.

---

## 8a. Consultation Model

Defined in [`backend/clinic/models.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/models.py). Holds per-visit notes and visit timestamps. Note the field is named **`visits`** (plural).

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `consultation_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing unique consultation ID. |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='consultations'` | Relational foreign key referencing `students.student_id`. |
| `consultation` | `TextField` | `blank=True, default=''` | Clinic consultation notes, diagnosis, and treatment provided. |
| `visits` | `DateTimeField` | `default=timezone.now` | Date and time of the clinic visit. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Record last-updated timestamp. |

### Database Metadata
* **Table Name**: `consultations`
* **Default Ordering**: `['-visits', '-consultation_id']`
* **Indexes**:
  * `idx_c_student_visit` on `(student_id, -visits)`
  * `idx_c_visit` on `(-visits)`

---

## 9. Health Status Model

Defined in [`backend/clinic/models.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/models.py). Health status records are managed through a full CRUD API consumed by the external Faculty System.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `status_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing unique health status record ID. |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='health_statuses'` | Relational foreign key referencing `students.student_id`. |
| `health_status` | `TextField` | `blank=True, default=''` | Health status details reported for the student. |
| `date` | `DateTimeField` | `default=timezone.now` | Date and time the health status was recorded. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Record last-updated timestamp. |

### Database Metadata
* **Table Name**: `health_statuses`
* **Default Ordering**: `['-date', '-status_id']`
* **Indexes**:
  * `idx_hs_student_date` on `(student_id, -date)`
  * `idx_hs_date` on `(-date)`

---

## 10. Student Relationships

`Student` is the parent of three child collections, each cascading on delete:

```text
Student (student_id = 2026001234)
  ├── HealthRecord (health_id = 1)
  ├── HealthRecord (health_id = 2)
  ├── Consultation (consultation_id = 1, visits = 2026-08-20)
  ├── Consultation (consultation_id = 2, visits = 2026-08-22)
  └── HealthStatus  (status_id  = 1, date   = 2026-08-25)
```

* **Relational Keys**: `health_records.student_id`, `consultations.student_id`, and `health_statuses.student_id` all reference `students.student_id`.
* **Reverse Lookups**: `student.health_records.all()`, `student.consultations.all()`, `student.health_statuses.all()`.
* **Cardinality**: all three are **One-to-Many**. `HealthRecord` and `Consultation` are **siblings** — neither references the other.
* **Cascade Behavior (`on_delete=models.CASCADE`)**: When a student is deleted, all associated health records, consultations, and health statuses are automatically deleted from PostgreSQL to prevent orphan records. Asserted by three model tests.

Full ER diagram and index rationale: [`docs/data-model.md`](docs/data-model.md).

---

## 11. API Documentation

Base URL: `http://127.0.0.1:8000`

### Discovery and Schema Endpoints

| Path | Purpose |
| :--- | :--- |
| `GET /` | Returns API metadata, status, and endpoint directory. |
| `GET /api/schema/` | OpenAPI 3 schema (JSON), generated by drf-spectacular. |
| `GET /api/schema/swagger-ui/` | Interactive Swagger UI. |
| `GET /api/schema/redoc/` | ReDoc documentation UI. |

---

### Session Authentication Endpoints (`/api/auth/`)

Implemented in [`backend/authentication/views.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/authentication/views.py). Session-cookie based.

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/auth/csrf/` | Obtain a CSRF token and set the CSRF cookie. | `AllowAny` |
| `POST` | `/api/auth/login/` | Authenticate with `username` / `password`, create a Django session. | `AllowAny` |
| `POST` | `/api/auth/logout/` | Destroy the current session. | `IsAuthenticated` |
| `GET` | `/api/auth/me/` | Return the current user's `id`, `username`, `email`, `is_staff`. | `IsAuthenticated` |

> [!CAUTION]
> These endpoints work, but **no clinic or integration viewset currently requires authentication**.
> Global `DEFAULT_PERMISSION_CLASSES` is `AllowAny`. See [integration.md §5](docs/integration.md#5-authentication-and-trust-boundaries).

---

### Student Endpoints (`/api/students/`)

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/students/` | List all students (supports search by student ID). | `200 OK` |
| `POST` | `/api/students/` | Create a new student (must provide `student_id`). | `201 Created`, `400 Bad Request` |
| `GET` | `/api/students/<student_id>/` | Retrieve a single student and their consultation history. | `200 OK`, `404 Not Found` |
| `PUT` | `/api/students/<student_id>/` | Fully update a student record. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `PATCH` | `/api/students/<student_id>/` | Partially update a student record. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/students/<student_id>/` | Delete student and cascade all their health records. | `204 No Content`, `404 Not Found` |

---

### Health Record Endpoints (`/api/health-records/`)

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health-records/` | List all health records across all students. | `200 OK` |
| `POST` | `/api/health-records/` | Create a health record (supply integer `student_id`). | `201 Created`, `400 Bad Request` |
| `GET` | `/api/health-records/<health_id>/` | Retrieve a specific health record. | `200 OK`, `404 Not Found` |
| `PUT` | `/api/health-records/<health_id>/` | Fully update a health record. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `PATCH` | `/api/health-records/<health_id>/` | Partially update a health record. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/health-records/<health_id>/` | Delete a health record. | `204 No Content`, `404 Not Found` |

---

### Nested Student Health Record Endpoints

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/students/<student_id>/health-records/` | Retrieve all health records for a specific student (ordered `-health_id`). | `200 OK`, `404 Not Found` |
| `POST` | `/api/students/<student_id>/health-records/` | Create a health record directly linked to the student (`student_id` injected from the path). | `201 Created`, `400 Bad Request`, `404 Not Found` |

---

### Consultation Endpoints (`/api/consultations/`)

Full CRUD for clinic consultation notes and visit dates.

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/consultations/` | List all consultations (supports `?student_id=` and `?search=`). | `200 OK` |
| `POST` | `/api/consultations/` | Create a consultation (supply integer `student_id`). | `201 Created`, `400 Bad Request` |
| `GET` | `/api/consultations/<consultation_id>/` | Retrieve a specific consultation. | `200 OK`, `404 Not Found` |
| `PUT` | `/api/consultations/<consultation_id>/` | Fully update a consultation. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `PATCH` | `/api/consultations/<consultation_id>/` | Partially update a consultation. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/consultations/<consultation_id>/` | Delete a consultation. | `204 No Content`, `404 Not Found` |

---

### Nested Student Consultation Endpoints

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/students/<student_id>/consultations/` | Retrieve a student's consultation history (ordered `-visits`, `-consultation_id`). | `200 OK`, `404 Not Found` |
| `POST` | `/api/students/<student_id>/consultations/` | Create a consultation linked to the student (`student_id` injected from the path). | `201 Created`, `400 Bad Request`, `404 Not Found` |

---

### Student Portal Health Record Endpoints (view-only)

Public, read-only endpoints exposed for the external **Student Portal System**. No create, update, or delete operations are available; `POST` / `PUT` / `PATCH` / `DELETE` return `405 Method Not Allowed`.

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/student-portal/health-records/` | List all available health records. | `200 OK` |
| `GET` | `/api/student-portal/health-records/<student_id>/` | Retrieve all health records for a specific student. Returns a **JSON array**, not a single object. | `200 OK`, `404 Not Found` |

> [!NOTE]
> Consultation notes are **not** available through this endpoint. They moved to the `Consultation`
> model, and no portal-facing consultation route exists. See
> [integration.md — AG-09](docs/integration.md#7-agreements-log).

---

### Health Status Endpoints (`/api/health-statuses/`)

Full CRUD endpoints consumed by the external **Faculty System**. Requires no authentication.

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health-statuses/` | List all health status records. | `200 OK` |
| `POST` | `/api/health-statuses/` | Create a health status (supply integer `student_id`). | `201 Created`, `400 Bad Request` |
| `GET` | `/api/health-statuses/<status_id>/` | Retrieve a specific health status record. | `200 OK`, `404 Not Found` |
| `PUT` | `/api/health-statuses/<status_id>/` | Fully update a health status record. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `PATCH` | `/api/health-statuses/<status_id>/` | Partially update a health status record. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/health-statuses/<status_id>/` | Delete a health status record. | `204 No Content`, `404 Not Found` |

---

## 12. API Search and Filtering

### Student Search & Filtering
Query parameters supported on `GET /api/students/`:
* `?search=<text>`: Match on `student_id`. **Digits only** — the filter applies only when the value `isdigit()`; a non-numeric value returns the unfiltered list rather than an empty one.

**Examples:**
```http
GET /api/students/?search=2026001234
```

### Health Record Search & Filtering
Query parameters supported on `GET /api/health-records/`:
* `?student_id=<id>`: Filter by integer student ID. Numeric values match exactly; non-numeric values fall through to an exact string match.
* `?blood_type=<type>`: Case-insensitive match on blood type.
* `?search=<text>`: Search across allergies, medical history, and student ID.

> [!CAUTION]
> **Known defect.** `?search=` is currently **broken** on this endpoint.
> [`views.py:283`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py) filters on
> `Q(consultations__consultation__icontains=search)`. `consultations` is a reverse relation on
> **Student**, not on `HealthRecord`, so the request raises `FieldError` and returns `500`.
> The correct path is `student__consultations__consultation`. No test covers this parameter, which
> is why the suite passes. Tracked in
> [architecture.md §6.3](docs/architecture.md#63-known-defects-found-while-verifying-this-document).

**Examples (once fixed):**
```http
GET /api/health-records/?student_id=2026001234
GET /api/health-records/?blood_type=O+
GET /api/health-records/?search=Asthma
```

### Consultation Search & Filtering
Query parameters supported on `GET /api/consultations/`:
* `?student_id=<id>`: Filter by student ID.
* `?search=<text>`: Search consultation notes; numeric values also match `student_id`.

**Examples:**
```http
GET /api/consultations/?student_id=2026001234
GET /api/consultations/?search=cough
```

### Health Status Filtering
`HealthStatusViewSet` does **not** override `get_queryset()`, so `GET /api/health-statuses/` supports no query parameters.

---

## 13. API Request and Response Examples

### 1. Create a Student (`POST /api/students/`)
**Request:**
```http
POST /api/students/
Content-Type: application/json

{
  "student_id": 2026001234
}
```

**Response (`201 Created`):**
```json
{
  "student_id": 2026001234,
  "health_records_count": 0,
  "consultations_count": 0,
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

### 2. Create a Health Record (`POST /api/health-records/`)
Supply the externally provided `student_id`. Note there is no `visit` or `consultation` field — those live in the Consultation model.

**Request:**
```http
POST /api/health-records/
Content-Type: application/json

{
  "student_id": 2026001234,
  "allergies": "Penicillin",
  "blood_type": "O+",
  "medical_history": "Mild asthma diagnosed in 2018",
  "medication": "Salbutamol 100mcg inhaler",
  "weight": "58.50",
  "height": "168.00"
}
```

**Response (`201 Created`):**
```json
{
  "health_id": 1,
  "student_id": 2026001234,
  "allergies": "Penicillin",
  "blood_type": "O+",
  "medical_history": "Mild asthma diagnosed in 2018",
  "medication": "Salbutamol 100mcg inhaler",
  "weight": "58.50",
  "height": "168.00",
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

### 3. Create a Consultation (`POST /api/consultations/`)
Visit date and notes are recorded here, not on the health record.

**Request:**
```http
POST /api/consultations/
Content-Type: application/json

{
  "student_id": 2026001234,
  "consultation": "Routine consultation for mild cough and allergy review.",
  "visits": "2026-08-22T14:47:00Z"
}
```

**Response (`201 Created`):**
```json
{
  "consultation_id": 1,
  "student_id": 2026001234,
  "consultation": "Routine consultation for mild cough and allergy review.",
  "visits": "2026-08-22T14:47:00Z",
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

### 4. Retrieve Student Details with Records (`GET /api/students/2026001234/`)
Uses `StudentDetailSerializer`, which nests **both** collections.

**Response (`200 OK`):**
```json
{
  "student_id": 2026001234,
  "health_records_count": 1,
  "consultations_count": 1,
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z",
  "health_records": [
    {
      "health_id": 1,
      "student_id": 2026001234,
      "allergies": "Penicillin",
      "blood_type": "O+",
      "medical_history": "Mild asthma diagnosed in 2018",
      "medication": "Salbutamol 100mcg inhaler",
      "weight": "58.50",
      "height": "168.00",
      "created_at": "2026-08-22T14:47:00.000000Z",
      "updated_at": "2026-08-22T14:47:00.000000Z"
    }
  ],
  "consultations": [
    {
      "consultation_id": 1,
      "student_id": 2026001234,
      "consultation": "Routine consultation for mild cough and allergy review.",
      "visits": "2026-08-22T14:47:00Z",
      "created_at": "2026-08-22T14:47:00.000000Z",
      "updated_at": "2026-08-22T14:47:00.000000Z"
    }
  ]
}
```

---

### 5. Student Portal — List Health Records for a Student (`GET /api/student-portal/health-records/2026001234/`)
Returns a **JSON array** of that student's health records.

**Response (`200 OK`):**
```json
[
  {
    "health_id": 1,
    "student_id": 2026001234,
    "allergies": "Penicillin",
    "blood_type": "O+",
    "medical_history": "Mild asthma diagnosed in 2018",
    "medication": "Salbutamol 100mcg inhaler",
    "weight": "58.50",
    "height": "168.00",
    "created_at": "2026-08-22T14:47:00.000000Z",
    "updated_at": "2026-08-22T14:47:00.000000Z"
  }
]
```

---

### 6. Create a Health Status (`POST /api/health-statuses/`)
**Request:**
```http
POST /api/health-statuses/
Content-Type: application/json

{
  "student_id": 2026001234,
  "health_status": "Stable",
  "date": "2026-09-18T10:00:00Z"
}
```

**Response (`201 Created`):**
```json
{
  "status_id": 1,
  "student_id": 2026001234,
  "health_status": "Stable",
  "date": "2026-09-18T10:00:00Z",
  "created_at": "2026-09-18T10:00:00.000000Z",
  "updated_at": "2026-09-18T10:00:00.000000Z"
}
```

---

## 14. Serializers and Validation

Implemented in [`backend/clinic/serializers.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py):

### [`StudentSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L113-L136)
* **Required Fields**: `student_id`
* **Read-Only Fields**: `health_records_count`, `consultations_count`, `created_at`, `updated_at`

### [`StudentDetailSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L139-L147)
* Extends `StudentSerializer` and adds nested, read-only `health_records[]` and `consultations[]`.
* Used for single-student detail responses.

### [`HealthRecordSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L10-L60)
* **Required Fields**: `student_id` (foreign key)
* **Optional Fields**: `allergies`, `blood_type`, `medical_history`, `medication`, `weight`, `height`
* **Read-Only Fields**: `health_id`, `created_at`, `updated_at`
* **Field Validations**:
  * `student_id`: Validated against existing `Student` records in PostgreSQL (returns `400 Bad Request` if invalid).
  * `weight`: Must be `> 0 kg` and `<= 500 kg`.
  * `height`: Must be `> 0 cm` and `<= 300 cm`.
  * `blood_type`: Validated against choices (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `Unknown`).

### [`ConsultationSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L63-L85)
* **Required Fields**: `student_id` (foreign key)
* **Optional Fields**: `consultation`, `visits`
* **Read-Only Fields**: `consultation_id`, `created_at`, `updated_at`
* **Field Validations**:
  * `student_id`: Validated against existing `Student` records in PostgreSQL (returns `400 Bad Request` if invalid).

### [`HealthStatusSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L88-L110)
* **Required Fields**: `student_id` (foreign key)
* **Optional Fields**: `health_status`, `date`
* **Read-Only Fields**: `status_id`, `created_at`, `updated_at`
* **Field Validations**:
  * `student_id`: Validated against existing `Student` records in PostgreSQL (returns `400 Bad Request` if invalid).
  * `health_status`: no controlled vocabulary — free text is accepted.

> **Naming note:** the model attribute is `student`, but every child serializer exposes it to
> clients as **`student_id`** via `PrimaryKeyRelatedField(source='student')`, matching the database
> column name.

---

## 15. Views and ViewSets

Implemented in [`backend/clinic/views.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py):

* **[`StudentViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L73)**:
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'student_id'`, `lookup_value_regex = r'[^/]+'`.
  * Dynamically swaps serializer: returns [`StudentDetailSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L139-L147) for single-student detail views and [`StudentSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L113-L136) for list views.
  * Uses `prefetch_related('health_records', 'consultations')` to prevent N+1 queries.
  * Implements `@action(detail=True, methods=['get', 'post'], url_path='health-records')` and `@action(detail=True, methods=['get', 'post'], url_path='consultations')` for nested operations. Both POST handlers inject `student_id` from the URL path.
* **[`HealthRecordViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L249)**:
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'health_id'`.
  * Uses `select_related('student')` to prevent N+1 database queries.
  * Overrides `get_queryset()` for `?student_id=`, `?blood_type=`, and `?search=` filtering (the `?search=` branch is defective — see §12).
* **[`StudentPortalHealthRecordViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L307)**:
  * View-only ViewSet for the external Student Portal System.
  * Inherits from `rest_framework.viewsets.ReadOnlyModelViewSet` (exposes only `GET` operations; no create/update/delete).
  * Uses `lookup_field = 'student_id'`; overrides `retrieve()` so the detail route returns a **list** of that student's health records rather than a single object.
  * Reuses [`HealthRecordSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L10-L60).
* **[`ConsultationViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L380)**:
  * Full CRUD ViewSet for clinic consultations and visit dates.
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'consultation_id'`.
  * Uses `select_related('student')`; overrides `get_queryset()` for `?student_id=` and `?search=`.
* **[`HealthStatusViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L457)**:
  * Full CRUD ViewSet consumed by the external Faculty System.
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'status_id'`.
  * Uses `select_related('student')`. Does **not** override `get_queryset()`, so it supports no query parameters.

## 16. Authentication, Permissions, CORS, and CSRF

### Authentication & Permissions
* **REST API (`/api/`)**: Configured with `AllowAny` permissions (`rest_framework.permissions.AllowAny`) in `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']`. **No clinic viewset requires authentication.**
* **Session auth (`/api/auth/`)**: `csrf` and `login` are `AllowAny`; `logout` and `me` require `IsAuthenticated`. Implemented in `backend/authentication/views.py`.
* **Django Admin (`/admin/`)**: Enforces session-based authentication with `django.contrib.auth`. Access requires active staff credentials (`is_staff=True`, `is_superuser=True`).

> [!CAUTION]
> The session-authentication app exists and functions, but it is not wired into any clinic or
> integration endpoint. Any client that can reach port 8000 can currently read every student's health
> records and write consultations.

### CORS (Cross-Origin Resource Sharing)
* Handled via `corsheaders.middleware.CorsMiddleware`, first in `MIDDLEWARE`.
* `CORS_ALLOW_ALL_ORIGINS = False`.
* Permitted origins are a **hardcoded list** in `backend/config/settings.py`:
  * `http://localhost:5173`, `http://127.0.0.1:5173` (Vite development server)
* `CORS_ALLOW_CREDENTIALS = True`.
* `CSRF_TRUSTED_ORIGINS` contains the same two origins.

> [!NOTE]
> `backend/.env.example` also lists `http://localhost:3000` and `http://127.0.0.1:3000`, but
> `CORS_ALLOWED_ORIGINS` in `settings.py` is a literal and is **not** read from the environment.
> Editing `.env` has no effect on CORS. `settings.py` supports an SQLite fallback via `DB_ENGINE`
> for local experimentation.

### CSRF Protection
* Django's `CsrfViewMiddleware` is active for admin session views. DRF REST views parse JSON payloads and operate cleanly with API clients.
* `GET /api/auth/csrf/` issues a CSRF token and sets the cookie for session-authenticated frontends.

---

## 17. Django Admin Portal

Configured in [`backend/clinic/admin.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py). **This is the only working user interface in the project.**

* **[`StudentAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L28-L50)**:
  * **List Display**: `student_id`, `created_at`, `updated_at`.
  * **Search**: `student_id`.
  * **Ordering**: `student_id`.
  * **Inlines**: `HealthRecordInline` (shows `health_id`, `blood_type`, `weight`, `height`, `allergies`) and `ConsultationInline` (shows `consultation_id`, `visits`, `consultation`), allowing staff to view and log records directly from the student's page.
  * **Read-Only**: `student_id`, `created_at`, `updated_at`.
  * **Fieldsets**: Student Identity; Timestamps (collapsed).
* **[`HealthRecordAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L53-L90)**:
  * **List Display**: `health_id`, `student`, `blood_type`, `weight`, `height`, `created_at`.
  * **Filters**: `blood_type`.
  * **Search**: `student__student_id`, `blood_type`, `allergies`, `medication`.
  * **Ordering**: `-health_id`.
  * **Raw ID Fields**: `student`.
  * **Fieldsets**: Student Reference; Vitals & Physical Stats; Medical Information; Timestamps (collapsed).
* **[`ConsultationAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L93-L123)**:
  * **List Display**: `consultation_id`, `student`, `visits`, `created_at`.
  * **Filters**: `visits`.
  * **Search**: `student__student_id`, `consultation`.
  * **Ordering**: `-visits`, `-consultation_id`.
  * **Raw ID Fields**: `student`.
* **[`HealthStatusAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L126-L157)**:
  * **List Display**: `status_id`, `student`, `health_status`, `date`, `created_at`.
  * **Filters**: `date`.
  * **Search**: `student__student_id`, `health_status`.
  * **Ordering**: `-date`, `-status_id`.
  * **Raw ID Fields**: `student`.

---

## 18. Migrations

Database schema changes are tracked in `backend/clinic/migrations/`:

* **`0001_initial.py`**: Created the initial `students` and `health_records` tables with relationships, checks, and indexes.
* **`0002_alter_student_student_id.py`**: Updated `Student.student_id` to an auto-incrementing `BigAutoField`.
* **`0003_remove_student_idx_student_name_and_more.py`**: Simplified `Student` model to only `student_id`, `created_at`, and `updated_at`. Changed `student_id` to manually supplied `BigIntegerField` primary key. Removed obsolete fields and indexes.
* **`0004_healthstatus.py`**: Created the `health_statuses` table with its foreign key to `students` and supporting indexes.
* **`0005_consultation.py`**: Created the `consultations` table; ran a `RunPython` data migration copying every `health_records.visit` / `.consultation` pair into a new `Consultation`; then dropped both columns from `health_records` and swapped the health-record indexes. Reversible, though the reverse is lossy for students with multiple consultations. See [ADR-0002](docs/decisions/0002-split-consultations-from-health-records.md).

### Migration Commands
* `python manage.py makemigrations`: Scans model files and generates new migration scripts.
* `python manage.py migrate`: Applies pending migration scripts to PostgreSQL.

> Developers should never create application tables with raw SQL — schema is managed exclusively by Django migrations.

---

## 19. Automated Test Suite

The test suite is located in [`backend/clinic/tests.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/tests.py) using DRF's `APITestCase`.

### Test Coverage Breakdown (**54 Tests Total**)
* **`StudentModelTests`** (2): Model instantiation with externally supplied `student_id`, string representation.
* **`HealthRecordModelTests`** (2): Model instantiation and FK association, `ON DELETE CASCADE` deletion.
* **`ConsultationModelTests`** (2): Model instantiation and FK association, `ON DELETE CASCADE` deletion.
* **`HealthStatusModelTests`** (2): Model instantiation and FK association, `ON DELETE CASCADE` deletion.
* **`StudentAPITests`** (8): `GET` list, search and filter, `POST` create with external `student_id`, `GET` single student, `GET` 404 handler, `PUT` full update, `PATCH` partial update, `DELETE` student.
* **`HealthRecordAPITests`** (8): `GET` list, `POST` create with integer `student_id`, non-existent student 400 rejection, negative weight rejection, `GET` single record, `PUT` full update, `PATCH` partial update, `DELETE` record.
* **`ConsultationAPITests`** (7): `GET` list, `POST` create with integer `student_id`, non-existent student 400 rejection, `GET` single consultation, `PUT` full update, `PATCH` partial update, `DELETE` consultation.
* **`HealthStatusAPITests`** (7): `GET` list, `POST` create with integer `student_id`, non-existent student 400 rejection, `GET` single status, `PUT` full update, `PATCH` partial update, `DELETE` status.
* **`StudentHealthRecordRelationshipEndpointTests`** (4): `GET` student records, `GET` 404 for missing student, `POST` create record via nested URL, `POST` 404 for missing student.
* **`StudentConsultationRelationshipEndpointTests`** (4): `GET` student consultations, `GET` 404 for missing student, `POST` create consultation via nested URL, `POST` 404 for missing student.
* **`StudentPortalHealthRecordAPITests`** (4): `GET` all records for the Student Portal API, `GET` a specific student's records, `GET` 404 for missing student, `POST` returns 405 (view-only).
* **`ErrorHandlingAndValidationTests`** (4): Duplicate student ID rejection, invalid blood type rejection, excessive weight/height rejection (>500kg / >300cm), API root discovery check.

### Verified Test Run
```text
Ran 54 tests in 1.776s

OK
Destroying test database for alias 'default'...
System check identified no issues (0 silenced).
```

> **Coverage gap:** no test exercises the `?search=` query parameter on `/api/health-records/`,
> which is the source of the defect described in §12.

---

## 20. Security and Data Integrity

* **ORM Parameterization**: All queries use Django ORM filter expressions and parameterized lookups; no raw SQL string concatenation is used.
* **Referential Integrity**: PostgreSQL enforces foreign keys (`FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE`) on all three child tables.
* **Input Sanitization**: Serializers enforce numeric limits on medical vitals, validate controlled choice lists, and verify primary key existence.
* **Centralized Exception Handling**: Implemented in [`backend/clinic/exceptions.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/exceptions.py) to intercept `IntegrityError` and `ValidationError`, returning clean JSON error responses rather than leaking database internals or stack traces. Registered as `REST_FRAMEWORK['EXCEPTION_HANDLER']`.

Every error response uses a uniform envelope:
```json
{
  "success": false,
  "status_code": 400,
  "errors": { "detail": "A record with this identifier already exists." }
}
```
`IntegrityError` is mapped to `400` rather than `500`, with distinct messages for unique-constraint and foreign-key violations. Unhandled exceptions log server-side and return a generic `500`. **Successful responses are not wrapped in this envelope** — clients must branch on HTTP status.

### Known security weaknesses

* **No authentication on clinical data.** `DEFAULT_PERMISSION_CLASSES` is `AllowAny`, so any client that can reach the port can read and write health records. The `/api/auth/` endpoints exist but are not enforced by any viewset.
* **`SECRET_KEY` has a hardcoded fallback** in `settings.py` identical to the value shipped in `.env.example`, so it is not environment-only in practice.
* **`ALLOWED_HOSTS` defaults to `localhost,127.0.0.1,*`** — the wildcard makes the explicit list decorative.

---

## 21. Environment Variables

Template provided in [`backend/.env.example`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/.env.example):

```ini
# Django Configuration
SECRET_KEY=django-insecure-4uipb%r-hr+7aq+2g7xtu(a6gnf=0s-^ql!b6^=q=vi8g+2kz4
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=clinic_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

Variables actually read from the environment in `settings.py`: `SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
(with `POSTGRES_*` fallbacks). Setting `DB_ENGINE` to a SQLite engine switches the database
configuration.

> [!CAUTION]
> `CORS_ALLOWED_ORIGINS` in `.env` is **not read** — the value in `settings.py` is a hardcoded list
> containing only the two `:5173` origins. See §16.

> [!CAUTION]
> The `.env` file contains sensitive local credentials and should never be committed to public version control repositories. `.gitignore` excludes `.env` and `*.env`.

---

## 22. Known Defects

Recorded rather than fixed; this documentation pass changed no application code. Full detail in
[`docs/architecture.md §6.3`](docs/architecture.md#63-known-defects-found-while-verifying-this-document).

| # | Defect | Location |
| :--- | :--- | :--- |
| 1 | `?search=` on `/api/health-records/` raises `FieldError` — filters on a reverse relation belonging to `Student`, not `HealthRecord`. Untested. | `views.py:283` |
| 2 | `urlpatterns` assigned twice; the first block is dead code | `config/urls.py` |
| 3 | `ALLOWED_HOSTS` default includes a `*` wildcard | `settings.py` |
| 4 | `.env.example` CORS origins are not read by `settings.py` | `settings.py` |
| 5 | `SECRET_KEY` hardcoded fallback matches the shipped `.env.example` value | `settings.py` |
| 6 | Non-numeric `?search=` on students returns the unfiltered list instead of nothing | `views.py:101` |
| 7 | `gen/` is a stale generated client predating the Consultation split | `gen/` |

---

## 23. Architecture Decision Records

Recorded in [`docs/decisions/`](docs/decisions/README.md):

| ADR | Title | Status |
| :--- | :--- | :--- |
| [0001](docs/decisions/0001-backend-framework-django-drf.md) | Backend framework — Django 6.1 with Django REST Framework | Accepted |
| [0002](docs/decisions/0002-split-consultations-from-health-records.md) | Split consultations into their own table | Accepted |
| [0003](docs/decisions/0003-externally-supplied-student-id.md) | Externally supplied `student_id` as the primary key | Accepted |
