# Integration

Documents how the IDSC Clinic System connects to the systems around it: which external parties are
integrated, what identifiers and ports are shared, and what has been formally agreed.

This file is deliberately explicit about the difference between **implemented** and **intended**
integrations, because several are described in the project README in terms the code does not yet
support.

Related documents: [architecture.md](architecture.md) · [data-model.md](data-model.md)

---

## 1. Integration Inventory

| # | System | Direction | Transport | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Registrar System | Inbound data supply | **Not implemented** — caller-supplied `student_id` via `POST /api/students/` | Convention only |
| 2 | Student Portal System | Outbound API | HTTP/JSON, read-only | **Implemented** |
| 3 | Faculty System | Outbound API | HTTP/JSON, full CRUD | **Implemented** |
| 4 | React Frontend | Inbound consumer | HTTP/JSON + CORS | Endpoint ready, **client not built** |
| 5 | PostgreSQL | Infrastructure | psycopg 3 over TCP 5432 | **Implemented** |
| 6 | Django Admin | Internal back-office | Session auth, same origin | **Implemented** |

---

## 2. External Systems in Detail

### 2.1 Registrar System — convention, not an integration

The project README states that student identifiers are supplied by an external Registrar. In the
codebase, this is realised as a **constraint, not a connection**:

- `Student.student_id` is `BigIntegerField(primary_key=True)` (`models.py:30`) — the database will
  not generate it
- Consequently `POST /api/students/` requires the caller to provide `student_id`

**There is no Registrar endpoint, webhook, scheduled import, or file parser anywhere in this
repository.** No code performs an outbound call to a Registrar. Any student record that exists was
created by someone POSTing it, or by Django Admin.

Implication for integrators: the Registrar contract is currently *manual*. If the Registrar is
expected to push data, that importer does not exist yet and must be built.

### 2.2 Student Portal System — view-only health records

Served by `StudentPortalHealthRecordViewSet` (`views.py:307`), a `ReadOnlyModelViewSet` registered at
`student-portal/health-records`:

| Method | Path | Response |
| :--- | :--- | :--- |
| `GET` | `/api/student-portal/health-records/` | Array of all health records |
| `GET` | `/api/student-portal/health-records/{student_id}/` | Array of that student's health records |

Because the class is read-only, `POST` / `PUT` / `PATCH` / `DELETE` return `405 Method Not Allowed`.
This is asserted by `test_post_not_allowed`.

Two behaviours the consumer must know:

1. The detail route returns a **JSON array**, not a single object. `retrieve()` is overridden
   (`views.py:319`) to fetch the `Student` with `get_object_or_404` and then serialise
   `student.health_records.all()`. An unknown `student_id` yields `404`.
2. Each item uses the full `HealthRecordSerializer` shape. Because `visit` and `consultation` were
   moved to the `Consultation` model, **consultation notes are no longer available through this
   endpoint**. If the Student Portal needs visit history, it must call
   `GET /api/students/{student_id}/consultations/` instead — but that endpoint is not currently
   designated as portal-facing. This is an unresolved integration gap worth confirming.

No authentication is required; global `AllowAny` applies.

### 2.3 Faculty System — health status CRUD

Served by `HealthStatusViewSet` (`views.py:457`), a full `ModelViewSet` at `health-statuses`:

| Method | Path |
| :--- | :--- |
| `GET` | `/api/health-statuses/` |
| `POST` | `/api/health-statuses/` |
| `GET` `PUT` `PATCH` `DELETE` | `/api/health-statuses/{status_id}/` |

The Faculty System writes health statuses; the clinic system reads them. `student_id` is required on
create and must reference an existing student.

No filtering parameters are implemented on this viewset — `HealthStatusViewSet` does not override
`get_queryset()`, unlike the health-record and consultation viewsets.

No authentication is required; global `AllowAny` applies.

### 2.4 React Frontend — not yet connected

The frontend at `frontend/` is the unmodified Vite + React starter. It makes no API calls, and
`frontend/vite.config.js` configures only the React plugin — no dev-server proxy and no API base
URL. There is no configured connection from the frontend to the backend.

CORS is configured to allow exactly two origins, `http://localhost:5173` and
`http://127.0.0.1:5173` (`settings.py`). `CSRF_TRUSTED_ORIGINS` matches.

---

## 3. Shared Identifiers

| Identifier | Type | Owner | Shared with | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `student_id` | `BigInteger` | Registrar (by convention) | Portal, Faculty, Clinic, all three child tables | The single join key across the whole system. Primary key of `students`, and the FK column in `health_records`, `consultations`, `health_statuses`. |
| `health_id` | `BigInteger` (auto) | Clinic | Student Portal (read-only) | Surrogate key; no external meaning. |
| `consultation_id` | `BigInteger` (auto) | Clinic | Clinic | Surrogate key. |
| `status_id` | `BigInteger` (auto) | Clinic | Faculty | Surrogate key; the Faculty System addresses records by this value. |
| Django user `id` | `BigInteger` (auto) | Clinic | Admin / session auth | `auth_user.id`; not exposed on clinical records. |

Key consequence: `student_id` is **externally supplied and immutable**. It is the shared key across
every integration, so its format and allocation belong to the Registrar, not to this project. The
serializers expose it under the name `student_id` on all child payloads, matching the column name.

The three child tables all use the FK column name `student_id`, so a raw SQL join across any of them
to `students` uses identically named columns.

---

## 4. Shared Ports and Network Surface

| Component | Host | Port | Protocol | Configured in |
| :--- | :--- | :--- | :--- | :--- |
| PostgreSQL | `localhost` | `5432` | TCP (psycopg 3) | `backend/.env` → `DB_PORT` |
| Django backend | `localhost` | `8000` | HTTP | `manage.py runserver` |
| Vite frontend | `localhost` | `5173` | HTTP | Vite default |
| Django admin | `localhost` | `8000/admin/` | HTTP (session) | same origin as backend |

Development DB connection (`backend/.env.example`): `clinic_db` on `localhost:5432` as user
`postgres`. The server runs in the Docker container `clinic-postgres` (PostgreSQL `16-alpine`).

Base API URL used throughout the docs: `http://127.0.0.1:8000`.

---

## 5. Authentication and Trust Boundaries

Current state, stated plainly because it affects every integration above:

| Surface | Auth |
| :--- | :--- |
| All `/api/` endpoints | **None** — `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.AllowAny']` |
| `/api/auth/logout/`, `/api/auth/me/` | Session required (`IsAuthenticated`) |
| `/api/auth/csrf/`, `/api/auth/login/` | Open (`AllowAny`) |
| `/admin/` | Django session, staff account required |

The session-authentication endpoints exist and work, but **no clinic or integration viewset requires
authentication**. Any client that can reach the port can read every student's health records and
write consultations. The four `/api/auth/` views are currently unused by the rest of the API.

This is a known gap, not an oversight to be documented as working. Before the system handles real
student medical data, `DEFAULT_PERMISSION_CLASSES` should be tightened and the read-only portal
endpoints granted explicitly.

---

## 6. Error Contract

Every error from any endpoint — including the external-facing ones — is normalised by
`custom_exception_handler` (`backend/clinic/exceptions.py`):

```json
{
  "success": false,
  "status_code": 400,
  "errors": { "detail": "A record with this identifier already exists." }
}
```

Integrators rely on this shape:

| Situation | Status | `errors` content |
| :--- | :--- | :--- |
| Validation failure (weight, height, blood type, missing FK) | `400` | Field-keyed messages from the serializer |
| Duplicate `student_id` | `400` | `detail` — translated from `IntegrityError`, DB message not leaked |
| FK violation | `400` | `detail` — "Referenced related record does not exist or cannot be modified." |
| Unknown primary key | `404` | `detail` — "The requested resource was not found." |
| Write to a read-only endpoint | `405` | DRF default, wrapped |
| Unhandled server error | `500` | Generic `detail`; real cause logged server-side only |

Successful responses are **not** wrapped in this envelope — they are plain DRF payloads. Clients must
branch on HTTP status.

---

## 7. Agreements Log

Records what has been agreed between the Clinic System and each external party, and — importantly —
which agreements are **not yet formalised**. Nothing in this log implies code that does not exist.

| ID | Parties | Agreement | Status |
| :--- | :--- | :--- | :--- |
| AG-01 | Registrar ↔ Clinic | `student_id` is externally supplied as the primary key; the database does not generate it | Enforced in code; allocation mechanism informal |
| AG-02 | Registrar ↔ Clinic | Student name, course, and contact data are **not** stored in the clinic system — identity only | Enforced (migration `0003` removed those columns) |
| AG-03 | Clinic ↔ Student Portal | Portal receives **read-only** health record access; no write operations exposed | Enforced via `ReadOnlyModelViewSet` |
| AG-04 | Clinic ↔ Student Portal | Portal detail endpoint returns an **array** for one student, not an object | Enforced (`retrieve()` override) |
| AG-05 | Clinic ↔ Student Portal | No authentication required for portal endpoints | Enforced (current state) — **needs review before production** |
| AG-06 | Clinic ↔ Faculty | Faculty receives full CRUD on health statuses; clinic system stores and serves them | Enforced via `ModelViewSet` |
| AG-07 | Clinic ↔ Faculty | `health_status` is free text with no controlled vocabulary | Enforced (no validator) |
| AG-08 | Clinic ↔ Faculty / Portal | Both integrations reference students by the shared `student_id`; no separate cross-system mapping table exists | Enforced (shared FK) |
| AG-09 | Clinic ↔ Portal | Whether portal consumers need consultation notes | **Unresolved** — notes moved to `consultations`, which is not portal-exposed |
| AG-10 | Clinic ↔ all consumers | Error responses use the `{success, status_code, errors}` envelope | Enforced by the custom handler |
| AG-11 | Clinic ↔ frontend | CORS restricted to `localhost:5173` and `127.0.0.1:5173` in development | Enforced in `settings.py`; `.env.example` lists extra origins that are **not** read |
| AG-12 | Clinic ↔ Registrar | Automated inbound feed from the Registrar | **Not agreed / not implemented** |

### 7.1 Open items

1. **AG-09** — the Consultation split removed consultation data from the portal-facing endpoint.
   `GET /api/student-portal/health-records/` no longer includes notes or visit dates, and no
   portal-facing consultation route exists. Unresolved.
2. **AG-05** — `AllowAny` on all clinical data. Unresolved.
3. **AG-12** — no Registrar inbound importer exists. Unresolved.

---

## 8. Cross-Cutting Notes

- **No message queue, event bus, or webhook** exists. All integration is request/response over HTTP.
- **No background jobs or scheduled tasks** are configured. No Celery, no cron.
- **`gen/`** is a generated Python client from an older schema and does not reflect the current
  contract — see [data-model.md §9](data-model.md#9-mock-data--generated-client-drift).