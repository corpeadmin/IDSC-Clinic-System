# IDSC Clinic System

IDSC Clinic System is a web-based system designed to streamline clinic operations by reducing manual work, organizing clinic processes, and making it easier for clinic workers to efficiently manage their daily tasks.

---

## 1. Project Overview

The **IDSC Clinic System** provides a centralized digital platform for managing student health records, consultations, physical measurements, and clinic visit histories.

### Core Objectives
* **Streamline Clinic Operations**: Eliminates paper-based clinic record keeping and manual logs.
* **Organize Student Medical Data**: Stores student profiles alongside chronological health records, vital stats, allergies, and consultation notes.
* **Efficient Lookup & History**: Enables clinic staff to search students by name, course, or section, and inspect visit histories instantly.

### Component Responsibilities
* **Backend (`backend/`)**: Built with Python and Django 6.1, exposing a RESTful JSON API using Django REST Framework (DRF). Handles business logic, input validation, relationship integrity, and database operations via Django ORM.
* **REST API (`/api/`)**: Provides CRUD endpoints for Students and Health Records, plus nested relationship endpoints for querying and creating records tied to specific students.
* **PostgreSQL (`clinic_db`)**: The relational database management system running in a Docker container (`clinic-postgres`). Enforces table constraints, foreign keys, database indexes, and auto-incrementing primary keys.
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
│         StudentViewSet  │  HealthRecordViewSet            │
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
│          students  │  health_records  │  auth_user        │
└───────────────────────────────────────────────────────────┘
```

### Layer Responsibilities
1. **Frontend**: Renders the UI, collects user inputs, and makes asynchronous JSON API requests to backend endpoints.
2. **Django REST API**: Authenticates requests, parses JSON payloads, runs serializer validations, handles exceptions gracefully, and returns HTTP status codes.
3. **Django ORM**: Translates Python model queries into parameterized SQL statements, safeguarding against SQL injection and maintaining relational constraints.
4. **PostgreSQL**: Persists tables, generates auto-incrementing integer sequence IDs (`student_id`, `health_id`), enforces foreign-key referential integrity (`ON DELETE CASCADE`), and optimizes search via composite B-tree indexes.

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
│       ├── tests.py                   # 31 automated unit & integration tests
│       ├── urls.py                    # Clinic API router and route definitions
│       ├── views.py                   # StudentViewSet & HealthRecordViewSet
│       └── migrations/                # Database migration history
│           ├── 0001_initial.py        # Initial table creation
│           └── 0002_alter_student_student_id.py # Auto-increment student_id migration
└── frontend/                          # Vite + React single-page frontend
    ├── index.html                     # HTML entry template
    ├── package.json                   # Frontend dependencies and npm scripts
    ├── vite.config.js                 # Vite bundler configuration
    ├── eslint.config.js               # ESLint configuration
    └── src/                           # Frontend source code
        ├── main.jsx                   # React application root mount point
        ├── App.jsx                    # Root UI component
        ├── App.css                    # Main application styling
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
            └── health_records (HealthRecord entity table)
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
| `student_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing integer ID generated by the database. |
| `first_name` | `CharField(max_length=100)` | Non-blank | Student's given first name. |
| `last_name` | `CharField(max_length=100)` | Non-blank | Student's family last name. |
| `birth_date` | `DateField` | `null=True, blank=True` | Date of birth (must not be in the future). |
| `sex` | `CharField(max_length=20)` | `choices=['Male', 'Female', 'Other']`, `blank=True` | Biological sex or gender. |
| `course` | `CharField(max_length=100)` | Non-blank | Degree program / course (e.g. BSIT, BSN, BSCS). |
| `section` | `CharField(max_length=50)` | Non-blank | Class section (e.g. 3A, 1-1). |
| `contact_no` | `CharField(max_length=30)` | `blank=True, default=''` | Contact or mobile phone number. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Record last-updated timestamp. |

### Database Metadata
* **Table Name**: `students`
* **Default Ordering**: `['student_id']`
* **Indexes**:
  * `idx_student_name` on `(last_name, first_name)`
  * `idx_student_course_sec` on `(course, section)`

> [!IMPORTANT]
> `student_id` is an **auto-incrementing integer primary key**. Clients must **NOT** supply `student_id` when creating a student. The database automatically assigns sequential integer IDs (`1, 2, 3, ...`).

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

## 9. Student ↔ Health Record Relationship

The data model implements a strict **One-to-Many** relationship:

```text
Student (student_id = 1)
  ├── HealthRecord (health_id = 1, visit = 2026-08-20)
  ├── HealthRecord (health_id = 2, visit = 2026-08-22)
  └── HealthRecord (health_id = 5, visit = 2026-08-25)
```

* **Relational Key**: `health_records.student_id` references `students.student_id`.
* **Reverse Lookup**: Access all visits for a student via `student.health_records.all()`.
* **Cascade Behavior (`on_delete=models.CASCADE`)**: When a student is deleted, all associated health records and visit histories are automatically deleted from PostgreSQL to prevent orphan records.

---

## 10. API Documentation

Base URL: `http://127.0.0.1:8000`

### Discovery Endpoint
* **`GET /`**: Returns API metadata, status, and endpoint directory.

---

### Student Endpoints (`/api/students/`)

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/students/` | List all students (supports search and filtering). | `200 OK` |
| `POST` | `/api/students/` | Create a new student (do not provide `student_id`). | `201 Created`, `400 Bad Request` |
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

## 11. API Search and Filtering

### Student Search & Filtering
Query parameters supported on `GET /api/students/`:
* `?search=<text>`: Case-insensitive search matching `first_name`, `last_name`, `course`, `section`, or exact numeric `student_id`.
* `?course=<course_name>`: Exact case-insensitive filter by course (e.g. `?course=BSIT`).
* `?section=<section_name>`: Exact case-insensitive filter by section (e.g. `?section=3A`).
* `?sex=<sex_value>`: Exact filter by sex (e.g. `?sex=Male`).

**Examples:**
```http
GET /api/students/?search=Juan
GET /api/students/?search=1
GET /api/students/?course=BS%20Information%20Technology&section=3A
```

### Health Record Search & Filtering
Query parameters supported on `GET /api/health-records/`:
* `?student_id=<id>`: Filter health records by integer student ID (e.g. `?student_id=1`).
* `?blood_type=<type>`: Filter health records by blood type (e.g. `?blood_type=O+`).
* `?search=<text>`: Case-insensitive search across student name, student ID, allergies, medical history, or consultation notes.

**Examples:**
```http
GET /api/health-records/?student_id=1
GET /api/health-records/?blood_type=O+
GET /api/health-records/?search=Asthma
```

---

## 12. API Request and Response Examples

### 1. Create a Student (`POST /api/students/`)
**Request:**
```http
POST /api/students/
Content-Type: application/json

{
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2003-05-15",
  "sex": "Male",
  "course": "BS Information Technology",
  "section": "3A",
  "contact_no": "09123456789"
}
```

**Response (`201 Created`):**
```json
{
  "student_id": 1,
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2003-05-15",
  "sex": "Male",
  "course": "BS Information Technology",
  "section": "3A",
  "contact_no": "09123456789",
  "health_records_count": 0,
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

### 2. Create a Health Record (`POST /api/health-records/`)
Supply the generated integer `student_id`:

**Request:**
```http
POST /api/health-records/
Content-Type: application/json

{
  "student_id": 1,
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
  "student_id": 1,
  "student_name": "Juan Dela Cruz",
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

### 3. Retrieve Student Details with Records (`GET /api/students/1/`)
**Response (`200 OK`):**
```json
{
  "student_id": 1,
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2003-05-15",
  "sex": "Male",
  "course": "BS Information Technology",
  "section": "3A",
  "contact_no": "09123456789",
  "health_records_count": 1,
  "health_records": [
    {
      "health_id": 1,
      "student_id": 1,
      "student_name": "Juan Dela Cruz",
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
  ],
  "created_at": "2026-08-22T14:47:00.000000Z",
  "updated_at": "2026-08-22T14:47:00.000000Z"
}
```

---

## 13. Serializers and Validation

Implemented in [`backend/clinic/serializers.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py):

### [`StudentSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L71-L135)
* **Required Fields**: `first_name`, `last_name`, `course`, `section`
* **Optional Fields**: `birth_date`, `sex`, `contact_no`
* **Read-Only Fields**: `student_id`, `health_records_count`, `created_at`, `updated_at`
* **Field Validations**:
  * `first_name` & `last_name`: Stripped and validated to ensure non-empty strings.
  * `course` & `section`: Stripped and validated to ensure non-empty strings.
  * `birth_date`: Rejects dates in the future (`birth_date > date.today()`).
  * `sex`: Validates against permitted choices (`Male`, `Female`, `Other`).

### [`HealthRecordSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L11-L68)
* **Required Fields**: `student_id` (foreign key)
* **Optional Fields**: `allergies`, `blood_type`, `medical_history`, `medication`, `weight`, `height`, `visit`, `consultation`
* **Read-Only Fields**: `health_id`, `student_name`, `created_at`, `updated_at`
* **Field Validations**:
  * `student_id`: Validated against active `Student` records in PostgreSQL (returns `400 Bad Request` if invalid).
  * `weight`: Must be `> 0 kg` and `<= 500 kg`.
  * `height`: Must be `> 0 cm` and `<= 300 cm`.
  * `blood_type`: Validated against choices (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `Unknown`).

---

## 14. Views and ViewSets

Implemented in [`backend/clinic/views.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py):

* **[`StudentViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L21-L95)**:
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'student_id'`.
  * Dynamically swaps serializer: returns [`StudentDetailSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L136-L144) for single-student detail views (including full visit history) and [`StudentSerializer`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/serializers.py#L71-L135) for list views.
  * Implements `@action(detail=True, methods=['get', 'post'], url_path='health-records')` for nested operations.
* **[`HealthRecordViewSet`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/views.py#L96-L137)**:
  * Inherits from `rest_framework.viewsets.ModelViewSet`.
  * Uses `lookup_field = 'health_id'`.
  * Uses `select_related('student')` to prevent N+1 database queries.

---

## 15. Authentication, Permissions, CORS, and CSRF

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

## 16. Django Admin Portal

Configured in [`backend/clinic/admin.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py):

* **[`StudentAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L19-L64)**:
  * **List Display**: `student_id`, `first_name`, `last_name`, `course`, `section`, `sex`, `contact_no`, `birth_date`, `created_at`.
  * **Filters**: `course`, `section`, `sex`.
  * **Search**: `student_id`, `first_name`, `last_name`, `course`, `section`, `contact_no`.
  * **Inline**: Includes [`HealthRecordInline`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L10-L16) allowing clinic staff to view and log health records directly from the student's page.
  * **Read-Only**: `student_id`, `created_at`, `updated_at`.
* **[`HealthRecordAdmin`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/admin.py#L66-L112)**:
  * **List Display**: `health_id`, `student`, `blood_type`, `visit`, `weight`, `height`, `created_at`.
  * **Filters**: `blood_type`, `visit`.
  * **Search**: `student__student_id`, `student__first_name`, `student__last_name`, `blood_type`, `allergies`, `medication`, `consultation`.
  * **Raw ID Fields**: `student`.

---

## 17. Migrations

Database schema changes are tracked in `backend/clinic/migrations/`:

* **`0001_initial.py`**: Created the initial `students` and `health_records` tables with relationships, checks, and indexes.
* **`0002_alter_student_student_id.py`**: Updated `Student.student_id` to an auto-incrementing `BigAutoField`.

### Migration Commands
* `python manage.py makemigrations`: Scans model files and generates new migration scripts.
* `python manage.py migrate`: Applies pending migration scripts to PostgreSQL.

---

## 18. Automated Test Suite

The test suite is located in [`backend/clinic/tests.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/tests.py) using DRF's `APITestCase`:

### Test Coverage Breakdown (**31 Tests Total**)
* **`StudentModelTests`** (2 tests): Model instantiation, auto-increment integer ID generation, full name property, `__str__` format.
* **`HealthRecordModelTests`** (2 tests): Model instantiation, FK association, Decimal vitals precision, `ON DELETE CASCADE` deletion test.
* **`StudentAPITests`** (9 tests): `GET` list, search by name/ID, filter by course, `POST` create without `student_id`, ignoring client-provided `student_id`, future birth date rejection, `GET` single student, `GET` 404 handler, `PUT` full update, `PATCH` partial update, `DELETE` student.
* **`HealthRecordAPITests`** (8 tests): `GET` list, `POST` create with integer `student_id`, non-existent student 400 rejection, negative weight rejection, `GET` single record, `PUT` full update, `PATCH` partial update, `DELETE` record.
* **`StudentHealthRecordRelationshipEndpointTests`** (4 tests): `GET` student records, `GET` 404 for missing student, `POST` create record via nested URL, `POST` 404 for missing student.
* **`ErrorHandlingAndValidationTests`** (5 tests): Blank student name validation, invalid sex choice rejection, invalid blood type rejection, excessive weight/height rejection (>500kg / >300cm), API root discovery check.

### Verified Test Run
```text
Ran 31 tests in 0.687s
OK
Destroying test database for alias 'default'...
System check identified no issues (0 silenced).
```

---

## 19. Security and Data Integrity

* **ORM Parameterization**: All queries use Django ORM filter expressions and parameterized lookups; no raw SQL string concatenation is used.
* **Referential Integrity**: PostgreSQL enforces foreign keys (`FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE`).
* **Input Sanitization**: Serializers strip whitespace, enforce numeric limits on medical vitals, validate controlled choice lists, and verify calendar constraints.
* **Centralized Exception Handling**: Implemented in [`backend/clinic/exceptions.py`](file:///C:/Users/alexa/PycharmProjects/IDSC%20Clinic%20System/backend/clinic/exceptions.py) to intercept `IntegrityError` and `ValidationError`, returning clean JSON error responses rather than leaking database internals or stack traces.
* **Secrets Separation**: Sensitive settings (`SECRET_KEY`, database passwords) are loaded via environment variables rather than hardcoded in source code.

---

## 20. Environment Variables

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
