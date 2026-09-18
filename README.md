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
* **REST API (`/api/`)**: Provides CRUD endpoints for Students and Health Records, plus nested relationship endpoints for querying and creating records tied to specific students. Also provides a view-only Health Record API for the Student Portal System and a full Health Status CRUD API for the Faculty System.
* **PostgreSQL (`clinic_db`)**: The relational database management system running in a Docker container (`clinic-postgres`). Enforces table constraints, foreign keys, database indexes, and externally supplied primary keys.
* **Django Admin (`/admin/`)**: Built-in administrative back-office portal with tabular inlines, multi-field search, and filtering for authorized clinic personnel.
* **Frontend (`frontend/`)**: Single-page application built with React 19 and Vite, designed to consume the backend REST API over HTTP/CORS.

---

## 2. Technology Stack

All technology versions match the project's actual configuration:

### Backend
* **Python**: `3.14.x`
* **Django**: `6.1`
* **Django REST Framework (DRF)**: `3.18.0`
* **PostgreSQL Driver (`psycopg`)**: `3.3.4` (using `psycopg[binary]`)
* **CORS Middleware (`django-cors-headers`)**: `4.9.0`
* **Environment Configuration (`python-dotenv`)**: `1.2.3`

### Database
* **PostgreSQL**: `16-alpine` (hosted via Docker container `clinic-postgres`)

### Frontend
* **React**: `19.2.8`
* **React DOM**: `19.2.8`
* **Vite**: `8.2.0`
* **Node.js / npm**: Node 18+ runtime environment

---

## 3. System Architecture

The application follows a clean layered architecture:

```text
┌───────────────────────────────────────────────────────────┐
│                 Frontend (React 19 + Vite)                │
│                 http://localhost:5173                     │
└─────────────────────────────┬─────────────────────────────┘
                               │ HTTP / JSON (CORS Enabled)
                               ▼
┌───────────────────────────────────────────────────────────┐
│             Django REST API (Views & ViewSets)            │
│   StudentViewSet  │  HealthRecordViewSet                  │
│   StudentPortalHealthRecordViewSet │ HealthStatusViewSet  │
└─────────────────────────────┬─────────────────────────────┘
                               │ Validated Data / Serializers
                               ▼
┌───────────────────────────────────────────────────────────┐
│               Django ORM (Models & QuerySets)             │
│            Student Model  │  HealthRecord Model           │
└─────────────────────────────┬─────────────────────────────┘
                               │ PostgreSQL Protocol (psycopg 3)
                               ▼
┌───────────────────────────────────────────────────────────┐
│        PostgreSQL Database (Docker: clinic-postgres)      │
│                     Database: clinic_db                   │
│      students │ health_records │ health_statuses │ auth_user  │
└───────────────────────────────────────────────────────────┘
```

### Layer Responsibilities
1. **Frontend**: Renders the UI, collects user inputs, and makes asynchronous JSON API requests to backend endpoints.
2. **Django REST API**: Authenticates requests, parses JSON payloads, runs serializer validations, handles exceptions gracefully, and returns HTTP status codes. Serves the clinic UI, the Student Portal System (view-only health records), and the Faculty System (health status CRUD).
3. **Django ORM**: Translates Python model queries into parameterized SQL statements, safeguarding against SQL injection and maintaining relational constraints.
4. **PostgreSQL**: Persists tables, stores externally supplied primary keys (`student_id`), enforces foreign-key referential integrity (`ON DELETE CASCADE`), and optimizes search via B-tree indexes.

---

## 4. Project Structure

```text
IDSC Clinic System/
├── README.md                          # Main technical & developer documentation
├── SETUP.md                           # Step-by-step installation, setup & troubleshooting guide
├── main.py                            # Standalone entry script
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
│   └── clinic/                        # Main Clinic Django application
│       ├── __init__.py
│       ├── admin.py                   # Django Admin model registrations & inlines
│       ├── apps.py                    # App configuration (ClinicConfig)
│       ├── exceptions.py              # Custom API exception handler
│       ├── models.py                  # Student & HealthRecord database models
│       ├── serializers.py             # DRF serializers & field validation logic
│       ├── tests.py                   # 28 automated unit & integration tests
│       ├── urls.py                    # Clinic API router and route definitions
│       ├── views.py                   # Students, Health Records, Student Portal, and Health Status viewsets
│       └── migrations/                # Database migration history
│           ├── 0001_initial.py        # Initial table creation
│           ├── 0002_alter_student_student_id.py # Auto-increment student_id migration
│           ├── 0003_remove_student_idx_student_name_and_more.py # Simplified student schema
│           └── 0004_healthstatus.py   # Health Status table creation
└── frontend/                          # Vite + React single-page frontend
    ├── index.html                     # HTML entry template
    ├── package.json                   # Frontend dependencies and npm scripts
    ├── vite.config.js                 # Vite bundler configuration
    ├── eslint.config.js               # ESLint configuration
    └── src/                           # Frontend source code
        ├── main.jsx                   # React application root mount point
        ├── App.jsx                    # Root UI component
        ├── App.css                    # Main application stylesheet
        ├── index.css                  # Global base stylesheet
        └── assets/                    # Static UI images and SVG logos
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
| `blood_type` | `CharField(max_length=10)` | `choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown']`, `blank=True` | Student blood group. |
| `medical_history` | `TextField` | `blank=True, default=''` | Chronic illnesses or past medical history. |
| `medication` | `TextField` | `blank=True, default=''` | Current medications and prescriptions. |
| `weight` | `DecimalField(5, 2)` | `null=True, blank=True`, `min=0.0, max=500.0` | Weight in kilograms (kg). |
| `height` | `DecimalField(5, 2)` | `null=True, blank=True`, `min=0.0, max=300.0` | Height in centimeters (cm). |
| `visit` | `DateTimeField` | `default=timezone.now` | Date and time of the clinic visit. |
| `consultation` | `TextField` | `blank=True, default=''` | Clinical consultation notes and diagnosis. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Record last-updated timestamp. |

### Database Metadata
* **Table Name**: `health_records`
* **Default Ordering**: `['-visit', '-health_id']`
* **Indexes**:
  * `idx_hr_student_visit` on `(student_id, -visit)`
  * `idx_hr_visit` on `(-visit)`

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

## 10. Student ↔ Health Record Relationship

The data model implements a strict **One-to-Many** relationship:

```text
Student (student_id = 2026001234)
  ├── HealthRecord (health_id = 1, visit = 2026-08-20)
  ├── HealthRecord (health_id = 2, visit = 2026-08-22)
  └── HealthRecord (health_id = 5, visit = 2026-08-25)
```

* **Relational Key**: `health_records.student_id` references `students.student_id`.
* **Reverse Lookup**: Access all visits for a student via `student.health_records.all()`.
* **Cascade Behavior (`on_delete=models.CASCADE`)**: When a student is deleted, all associated health records and visit histories are automatically deleted from PostgreSQL to prevent orphan records.

---

## 11. API Documentation

Base URL: `http://127.0.0.1:8000`

### Discovery Endpoint
* **`GET /`**: Returns API metadata, status, and endpoint directory.

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
| `GET` | `/api/students/<student_id>/health-records/` | Retrieve all health records for a specific student. | `200 OK`, `404 Not Found` |
| `POST` | `/api/students/<student_id>/health-records/` | Create a health record directly linked to the student. | `201 Created`, `400 Bad Request`, `404 Not Found` |

---

### Student Portal Health Record Endpoints (view-only)

Public, read-only endpoints exposed for the external **Student Portal System**. No create, update, or delete operations are available. Requires no authentication.

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/student-portal/health-records/` | List all available health records. | `200 OK` |
| `GET` | `/api/student-portal/health-records/<student_id>/` | Retrieve all health records for a specific student. | `200 OK`, `404 Not Found` |

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
* `?search=<text>`: Exact or partial match on `student_id`.

**Examples:**
```http
GET /api/students/?search=2026001234
```

### Health Record Search & Filtering
Query parameters supported on `GET /api/health-records/`:
* `?student_id=<id>`: Filter health records by integer student ID (e.g. `?student_id=2026001234`).
* `?blood_type=<type>`: Filter health records by blood type (e.g. `?blood_type=O+`).
* `?search=<text>`: Case-insensitive search across allergies, consultation notes, or medical history.

**Examples:**
```http
GET /api/health-records/?student_id=2026001234
GET /api/health-records/?blood_type=O+
GET /api/health-records/?search=Asthma
```

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
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

### 2. Create a Health Record (`POST /api/health-records/`)
Supply the externally provided `student_id`:

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
  "height": "168.00",
  "consultation": "Routine consultation for mild cough and allergy review."
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
  "visit": "2026-08-22T14:47:00.000000Z",
  "consultation": "Routine consultation for mild cough and allergy review.",
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

### 3. Retrieve Student Details with Records (`GET /api/students/2026001234/`)
**Response (`200 OK`):**
```json
{
  "student_id": 2026001234,
  "health_records_count": 1,
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
      "visit": "2026-08-22T14:47:00.000000Z",
      "consultation": "Routine consultation for mild cough and allergy review.",
      "created_at": "2026-08-22T14:47:00.000000Z",
      "updated_at": "2026-08-22T14:47:00.000000Z"
    }
  ]
}
```

---

### 4. Student Portal — List Health Records for a Student (`GET /api/student-portal/health-records/2026001234/`)
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
    "visit": "2026-08-22T14:47:00.000000Z",
    "consultation": "Routine consultation for mild cough and allergy review.",
    "created_at": "2026-08-22T14:47:00.000000Z",
    "updated_at": "2026-08-22T14:47:00.000000Z"
  }
]
```

---

### 5. Create a Health Status (`POST /api/health-statuses/`)
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

### [`StudentSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L65-L83)
* **Required Fields**: `student_id`
* **Read-Only Fields**: `health_records_count`, `created_at`, `updated_at`

### [`HealthRecordSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L11-L68)
* **Required Fields**: `student_id` (foreign key)
* **Optional Fields**: `allergies`, `blood_type`, `medical_history`, `medication`, `weight`, `height`, `visit`, `consultation`
* **Read-Only Fields**: `health_id`, `created_at`, `updated_at`
* **Field Validations**:
  * `student_id`: Validated against active `Student` records in PostgreSQL (returns `400 Bad Request` if invalid).
  * `weight`: Must be `> 0 kg` and `<= 500 kg`.
  * `height`: Must be `> 0 cm` and `<= 300 cm`.
  * `blood_type`: Validated against choices (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `Unknown`).

### [`HealthStatusSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L96-L113)
* **Required Fields**: `student_id` (foreign key)
* **Optional Fields**: `health_status`, `date`
* **Read-Only Fields**: `status_id`, `created_at`, `updated_at`
* **Field Validations**:
  * `student_id`: Validated against active `Student` records in PostgreSQL (returns `400 Bad Request` if invalid).

---

## 15. Views and ViewSets

Implemented in [`backend/clinic/views.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py):

* **[`StudentViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py)**:
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'student_id'`.
  * Dynamically swaps serializer: returns [`StudentDetailSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L86-L93) for single-student detail views (including full visit history) and [`StudentSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L65-L83) for list views.
  * Implements `@action(detail=True, methods=['get', 'post'], url_path='health-records')` for nested operations.
* **[`HealthRecordViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py)**:
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'health_id'`.
  * Uses `select_related('student')` to prevent N+1 database queries.
* **[`StudentPortalHealthRecordViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py)**:
  * View-only ViewSet for the external Student Portal System.
  * Inherits from `rest_framework.viewsets.ReadOnlyModelViewSet` (exposes only `GET` operations; no create/update/delete).
  * Uses `lookup_field = 'student_id'`; detail route returns all health records for the requested student.
  * Reuses [`HealthRecordSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L11-L63).
* **[`HealthStatusViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py)**:
  * Full CRUD ViewSet consumed by the external Faculty System.
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'status_id'`.
  * Uses `select_related('student')` to prevent N+1 database queries.

## 16. Authentication, Permissions, CORS, and CSRF

### Authentication & Permissions
* **REST API (`/api/`)**: Configured with `AllowAny` permissions (`rest_framework.permissions.AllowAny`). Endpoints are accessible for clinic client integration without token/session barriers.
* **Django Admin (`/admin/`)**: Enforces session-based authentication with `django.contrib.auth`. Access requires active staff credentials (`is_staff=True`, `is_superuser=True`).

### CORS (Cross-Origin Resource Sharing)
* Handled via `corsheaders.middleware.CorsMiddleware`.
* Permitted development origins configured in `backend/config/settings.py` / `.env`:
  * `http://localhost:5173`, `http://127.0.0.1:5173` (Vite development server)
  * `http://localhost:3000`, `http://127.0.0.1:3000`
* `CORS_ALLOW_CREDENTIALS = True`

### CSRF Protection
* Django's `CsrfViewMiddleware` is active for admin session views. DRF REST views parse JSON payloads and operate cleanly with API clients.

---

## 17. Django Admin Portal

Configured in [`backend/clinic/admin.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py):

* **[`StudentAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L19-L64)**:
  * **List Display**: `student_id`, `created_at`, `updated_at`.
  * **Search**: `student_id`.
  * **Inline**: Includes [`HealthRecordInline`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L10-L16) allowing clinic staff to view and log health records directly from the student's page.
  * **Read-Only**: `student_id`, `created_at`, `updated_at`.
* **[`HealthRecordAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py)**:
  * **List Display**: `health_id`, `student`, `blood_type`, `visit`, `weight`, `height`, `created_at`.
  * **Filters**: `blood_type`, `visit`.
  * **Search**: `student__student_id`, `blood_type`, `allergies`, `medication`, `consultation`.
  * **Raw ID Fields**: `student`.
* **[`HealthStatusAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py)**:
  * **List Display**: `status_id`, `student`, `health_status`, `date`, `created_at`.
  * **Filters**: `date`.
  * **Search**: `student__student_id`, `health_status`.
  * **Raw ID Fields**: `student`.

---

## 18. Migrations

Database schema changes are tracked in `backend/clinic/migrations/`:

* **`0001_initial.py`**: Created the initial `students` and `health_records` tables with relationships, checks, and indexes.
* **`0002_alter_student_student_id.py`**: Updated `Student.student_id` to an auto-incrementing `BigAutoField`.
* **`0003_remove_student_idx_student_name_and_more.py`**: Simplified `Student` model to only `student_id`, `created_at`, and `updated_at`. Changed `student_id` to manually supplied `BigIntegerField` primary key. Removed obsolete fields and indexes.
* **`0004_healthstatus.py`**: Created the `health_statuses` table with its foreign key to `students` and supporting indexes.

### Migration Commands
* `python manage.py makemigrations`: Scans model files and generates new migration scripts.
* `python manage.py migrate`: Applies pending migration scripts to PostgreSQL.

---

## 19. Automated Test Suite

The test suite is located in [`backend/clinic/tests.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/tests.py) using DRF's `APITestCase`:

### Test Coverage Breakdown (**41 Tests Total**)
* **`StudentModelTests`** (2 tests): Model instantiation with externally supplied `student_id`, timestamp population, string representation.
* **`HealthRecordModelTests`** (2 tests): Model instantiation, FK association, Decimal vitals precision, `ON DELETE CASCADE` deletion test.
* **`StudentAPITests`** (7 tests): `GET` list, search by student ID, `POST` create with external `student_id`, `GET` single student, `GET` 404 handler, `PUT` full update, `PATCH` partial update, `DELETE` student.
* **`HealthRecordAPITests`** (8 tests): `GET` list, `POST` create with integer `student_id`, non-existent student 400 rejection, negative weight rejection, `GET` single record, `PUT` full update, `PATCH` partial update, `DELETE` record.
* **`StudentHealthRecordRelationshipEndpointTests`** (4 tests): `GET` student records, `GET` 404 for missing student, `POST` create record via nested URL, `POST` 404 for missing student.
* **`StudentPortalHealthRecordAPITests`** (4 tests): `GET` all records for the Student Portal API, `GET` a specific student's records, `GET` 404 for missing student, `POST` returns 405 (view-only).
* **`HealthStatusModelTests`** (2 tests): Health status model creation, FK relationship, `ON DELETE CASCADE` deletion test.
* **`HealthStatusAPITests`** (7 tests): `GET` list, `POST` create with integer `student_id`, non-existent student 400 rejection, `GET` single status, `PUT` full update, `PATCH` partial update, `DELETE` status.
* **`ErrorHandlingAndValidationTests`** (5 tests): Duplicate student ID rejection, invalid blood type rejection, excessive weight/height rejection (>500kg / >300cm), API root discovery check.

### Verified Test Run
```text
Ran 41 tests in 2.116s
OK
Destroying test database for alias 'default'...
System check identified no issues (0 silenced).
```

---

## 20. Security and Data Integrity

* **ORM Parameterization**: All queries use Django ORM filter expressions and parameterized lookups; no raw SQL string concatenation is used.
* **Referential Integrity**: PostgreSQL enforces foreign keys (`FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE`).
* **Input Sanitization**: Serializers enforce numeric limits on medical vitals, validate controlled choice lists, and verify primary key existence.
* **Centralized Exception Handling**: Implemented in [`backend/clinic/exceptions.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/exceptions.py) to intercept `IntegrityError` and `ValidationError`, returning clean JSON error responses rather than leaking database internals or stack traces.
* **Secrets Separation**: Sensitive settings (`SECRET_KEY`, database passwords) are loaded via environment variables rather than hardcoded in source code.

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

> [!CAUTION]
> The `.env` file contains sensitive local credentials and should never be committed to public version control repositories.
