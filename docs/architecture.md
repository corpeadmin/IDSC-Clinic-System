# Architecture

Scope: documents the system **as it exists in the repository at the time of writing**. Every claim
below is traceable to a file. Where something is *not* implemented, it is called out explicitly in
[Current Implementation Status](#current-implementation-status) rather than described aspirationally.

Related documents:

- [data-model.md](data-model.md) — entities, fields, ER diagram
- [integration.md](integration.md) — external systems, shared IDs and ports, agreements log
- [design-system.md](design-system.md) — UI tokens and module UI details
- [decisions/](decisions/) — architecture decision records

---

## 1. System Context

The IDSC Clinic System is a Django REST backend that owns student health data. It serves three
distinct consumers, plus an administrative back-office:

```text
                    ┌──────────────────────────────┐
                    │      Registrar System        │
                    │  (external, not in repo)     │
                    │  supplies student_id         │
                    └──────────────┬───────────────┘
                                   │ student_id supplied
                                   │ (convention, no inbound API)
                                   ▼
┌────────────────┐   HTTP/JSON   ┌───────────────────────────────────────────┐
│ Student Portal │──────────────▶│                                           │
│ System         │  view-only    │                                           │
│ (external)     │◀──────────────│                                           │
└────────────────┘               │                                           │
                                 │   IDSC Clinic System API                 │
┌────────────────┐   HTTP/JSON   │   (Django 6.1 + DRF, port 8000)          │
│ Faculty System │──────────────▶│                                           │
│ (external)     │◀──────────────│   /api/students/                         │
└────────────────┘  full CRUD    │   /api/health-records/                   │
                                 │   /api/consultations/                    │
┌────────────────┐  session auth  │   /api/health-statuses/                  │
│ Django Admin   │──────────────▶│   /api/student-portal/health-records/    │
│ (in-project)   │◀──────────────│   /api/auth/                             │
└────────────────┘               │   /admin/                                │
                                 │   /api/schema/ (+ swagger-ui, redoc)     │
┌────────────────┐  HTTP/CORS     │                                           │
│ React Frontend │──────────────▶│                                           │
│ (Vite, :5173)  │  ⚠ not wired  │                                           │
└────────────────┘               └─────────────────────┬─────────────────────┘
                                                        │ psycopg 3
                                                        ▼
                                        ┌───────────────────────────────┐
                                        │ PostgreSQL 16-alpine          │
                                        │ Docker container              │
                                        │ `clinic-postgres`             │
                                        │ db `clinic_db`, port 5432     │
                                        └───────────────────────────────┘
```

### 1.1 The Registrar integration is a convention, not an endpoint

The README describes "an external Registrar system" that supplies student identifiers. There is
**no inbound endpoint, webhook, or file feed for the Registrar in the codebase**. What exists is:

- `Student.student_id` is a `BigIntegerField` declared `primary_key=True`
  ([`backend/clinic/models.py:30`](../backend/clinic/models.py#L30)) — it is *not* auto-generated
- `POST /api/students/` therefore requires the caller to supply `student_id`

So the integration is a **caller obligation**, satisfied by whoever POSTs the student. There is no
code path in this repository that contacts a Registrar. This distinction is preserved in
[integration.md](integration.md) so the agreement log is not read as implying an implemented feed.

---

## 2. Backend Layers

The backend is a standard Django/DRF layered arrangement. Layer boundaries are enforced by Django's
app and module structure rather than by explicit interfaces.

```text
┌──────────────────────────────────────────────────────────────────────┐
│ URL / ROUTING                          backend/config/urls.py        │
│   /            → api_root_view (discovery JSON)                     │
│   /admin/     → django.contrib.admin                                 │
│   /api/auth/  → authentication.urls                                  │
│   /api/       → clinic.urls (DefaultRouter)                         │
│   /api/schema/→ drf-spectacular schema + Swagger UI + ReDoc         │
├──────────────────────────────────────────────────────────────────────┤
│ VIEWS / VIEWSETS                       backend/clinic/views.py       │
│   StudentViewSet             (views.py:73)                            │
│   HealthRecordViewSet        (views.py:249)                           │
│   StudentPortalHealthRecordViewSet (views.py:307)                    │
│   ConsultationViewSet        (views.py:380)                           │
│   HealthStatusViewSet        (views.py:457)                           │
│   authentication/views.py — csrf, login, logout, me                  │
├──────────────────────────────────────────────────────────────────────┤
│ SERIALIZERS                            backend/clinic/serializers.py │
│   input validation, FK resolution, response shaping                 │
├──────────────────────────────────────────────────────────────────────┤
│ EXCEPTION HANDLER                      backend/clinic/exceptions.py │
│   custom_exception_handler — wraps all errors into one envelope      │
├──────────────────────────────────────────────────────────────────────┤
│ MODELS / ORM                           backend/clinic/models.py      │
│   Student, HealthRecord, Consultation, HealthStatus                  │
├──────────────────────────────────────────────────────────────────────┤
│ DATABASE                               PostgreSQL via psycopg 3      │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.1 Layer responsibilities

| Layer | File(s) | Responsibility |
| :--- | :--- | :--- |
| Routing | `backend/config/urls.py` | Maps URL prefixes to apps; serves the discovery document at `/` |
| Routing (API) | `backend/clinic/urls.py` | `DefaultRouter` registration of five viewsets under `/api/` |
| Views | `backend/clinic/views.py` | CRUD dispatch, `get_queryset()` filtering, nested `@action` endpoints |
| Serializers | `backend/clinic/serializers.py` | Field-level validation, FK resolution via `PrimaryKeyRelatedField`, computed counts |
| Errors | `backend/clinic/exceptions.py` | Converts DRF / Django / DB exceptions into a uniform JSON envelope |
| Models | `backend/clinic/models.py` | Table shape, constraints, indexes, `on_delete` behaviour |
| Admin | `backend/clinic/admin.py` | Staff back-office with inlines, filters, search, fieldsets |

---

## 3. API Surface

Registered in [`backend/clinic/urls.py`](../backend/clinic/urls.py) via `DefaultRouter`:

| Prefix | ViewSet | Base class | `lookup_field` |
| :--- | :--- | :--- | :--- |
| `students` | `StudentViewSet` | `ModelViewSet` | `student_id` |
| `health-records` | `HealthRecordViewSet` | `ModelViewSet` | `health_id` |
| `student-portal/health-records` | `StudentPortalHealthRecordViewSet` | `ReadOnlyModelViewSet` | `student_id` |
| `consultations` | `ConsultationViewSet` | `ModelViewSet` | `consultation_id` |
| `health-statuses` | `HealthStatusViewSet` | `ModelViewSet` | `status_id` |

Generated schema (`openapi.json` / `openapi.yaml`, last regenerated 2026-09-22) lists **16 paths**
and **15 component schemas**, confirming this table matches the served contract.

### 3.1 Full endpoint inventory

Students:

| Method | Path | Notes |
| :--- | :--- | :--- |
| `GET` | `/api/students/` | Optional `?search=`; **digits only**, exact match (`views.py:101-104`) |
| `POST` | `/api/students/` | Requires externally supplied `student_id` |
| `GET` `PUT` `PATCH` `DELETE` | `/api/students/{student_id}/` | Detail returns nested records + consultations |
| `GET` | `/api/students/{student_id}/health-records/` | Ordered `-health_id` (`views.py:132`) |
| `POST` | `/api/students/{student_id}/health-records/` | Injects `student_id` from path (`views.py:139`) |
| `GET` | `/api/students/{student_id}/consultations/` | Ordered `-visits, -consultation_id` (`views.py:172`) |
| `POST` | `/api/students/{student_id}/consultations/` | Injects `student_id` from path (`views.py:179`) |

Health records:

| Method | Path | Notes |
| :--- | :--- | :--- |
| `GET` | `/api/health-records/` | `?student_id=`, `?blood_type=`, `?search=` — see known issue below |
| `POST` | `/api/health-records/` | `student_id` required in body |
| `GET` `PUT` `PATCH` `DELETE` | `/api/health-records/{health_id}/` | |

Consultations:

| Method | Path | Notes |
| :--- | :--- | :--- |
| `GET` | `/api/consultations/` | `?student_id=`, `?search=` |
| `POST` | `/api/consultations/` | `student_id` required in body |
| `GET` `PUT` `PATCH` `DELETE` | `/api/consultations/{consultation_id}/` | |

Student Portal (view-only, `ReadOnlyModelViewSet`):

| Method | Path | Notes |
| :--- | :--- | :--- |
| `GET` | `/api/student-portal/health-records/` | All records |
| `GET` | `/api/student-portal/health-records/{student_id}/` | Overridden `retrieve()` (`views.py:319`) — returns a **list** for one student, not a single object |

Health statuses (Faculty System):

| Method | Path | Notes |
| :--- | :--- | :--- |
| `GET` | `/api/health-statuses/` | |
| `POST` | `/api/health-statuses/` | `student_id` required in body |
| `GET` `PUT` `PATCH` `DELETE` | `/api/health-statuses/{status_id}/` | |

Session authentication:

| Method | Path | Permission | Source |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/auth/csrf/` | `AllowAny` | `authentication/views.py:12` |
| `POST` | `/api/auth/login/` | `AllowAny` | `authentication/views.py:25` |
| `POST` | `/api/auth/logout/` | `IsAuthenticated` | `authentication/views.py:80` |
| `GET` | `/api/auth/me/` | `IsAuthenticated` | `authentication/views.py:96` |

Documentation and discovery:

| Path | Purpose | Source |
| :--- | :--- | :--- |
| `/` | Discovery JSON listing every endpoint | `config/urls.py:10` |
| `/api/schema/` | OpenAPI 3 schema (JSON) | `config/urls.py` `SpectacularAPIView` |
| `/api/schema/swagger-ui/` | Swagger UI | `config/urls.py` |
| `/api/schema/redoc/` | ReDoc | `config/urls.py` |
| `/admin/` | Django admin | `config/urls.py` |

### 3.2 Error envelope

Every error response is normalised by `custom_exception_handler`
([`backend/clinic/exceptions.py:20`](../backend/clinic/exceptions.py#L20)), wired in via
`REST_FRAMEWORK['EXCEPTION_HANDLER']`:

```json
{
  "success": false,
  "status_code": 400,
  "errors": { "detail": "..." }
}
```

`IntegrityError` is translated to `400` rather than `500`, with distinct messages for unique-constraint
and foreign-key violations (`exceptions.py:72-80`). Unhandled exceptions log server-side and return a
generic `500` so internals are not leaked (`exceptions.py:92-99`).

> **Note:** successful responses are *not* wrapped in this envelope — they use plain DRF shapes. Any
> client must therefore branch on HTTP status, not on the presence of `success`.

---

## 4. Request Lifecycle

For `POST /api/health-records/`:

1. **CORS preflight / header handling** — `corsheaders.middleware.CorsMiddleware`, first in
   `MIDDLEWARE` (`settings.py`).
2. **Routing** — `DefaultRouter` dispatches to `HealthRecordViewSet.create()`.
3. **Permission check** — `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.AllowAny']`.
   Unauthenticated writes are currently permitted.
4. **Validation** — `HealthRecordSerializer` resolves `student_id` through
   `PrimaryKeyRelatedField(queryset=Student.objects.all())` (`serializers.py:17`); an unknown ID
   yields `400` before any write.
5. **Field validators** — `validate_weight` (0–500 kg), `validate_height` (0–300 cm),
   `validate_blood_type` against `BloodTypeChoices` (`serializers.py:39-60`).
6. **Persistence** — Django ORM emits parameterised SQL over psycopg 3.
7. **Response** — `201` with serialised payload.

Errors at any step pass through `custom_exception_handler`.

---

## 5. User Interfaces

Two surfaces exist. Neither is a custom-built clinic UI.

### 5.1 Django Admin — the only working UI

`/admin/` is framework-generated and fully functional. Configured in
[`backend/clinic/admin.py`](../backend/clinic/admin.py) with list displays, filters, search fields,
grouped fieldsets, `raw_id_fields` on every foreign key, and `HealthRecordInline` +
`ConsultationInline` embedded in the student change page. Session-authenticated, `is_staff` required.

### 5.2 React frontend — starter template, no clinic UI

`frontend/src/App.jsx` (122 lines) is the unmodified Vite + React starter landing page — a `count`
state counter, `hero.png`, React and Vite logos, and links to vite.dev, react.dev, GitHub, Discord,
X, and Bluesky. `App.css` and `index.css` style only that template. There is no clinic UI, no
routing, no API client, and no state management.

`frontend/vite.config.js` contains only the React plugin — **no dev-server proxy and no API base URL
are configured**, so the frontend has no configured path to the backend. No `fetch` or `axios` call
exists anywhere in `frontend/src`.

**No prototype screens have been designed, so there is no screen-to-endpoint mapping to document.**
The endpoint inventory in §3.1 is the complete list of what the API offers.

---

## 6. Current Implementation Status

### 6.1 Complete and verified

- Five viewsets with full CRUD, registered under `/api/` — matches `openapi.json`
- Four models with foreign keys, indexes, and `ON DELETE CASCADE` — see [data-model.md](data-model.md)
- Migration chain `0001` → `0005`, including the `visit`/`consultation` split and its data migration
- Custom exception handler producing a uniform error envelope
- Session authentication app (`csrf`, `login`, `logout`, `me`)
- Django admin with inlines for all four models
- OpenAPI schema generation via drf-spectacular
- **54 automated tests, all passing** (`python manage.py test clinic`)

### 6.2 Not implemented

| Area | Evidence |
| :--- | :--- |
| Frontend UI | `App.jsx` is the Vite template; no API calls, no router |
| Frontend→backend wiring | `vite.config.js` has no proxy or base URL |
| API client / type definitions | No `fetch`/axios usage anywhere in `frontend/src` |
| Screenshots of main screens | Nothing to capture; no screens exist |
| Figma / class design system | No Figma file or equivalent is referenced in the repo |
| Authentication enforcement on `/api/` | `AllowAny` globally; auth endpoints exist but no viewset requires them |
| Registrar inbound integration | No endpoint, webhook, or import job — see §1.1 |

### 6.3 Known defects found while verifying this document

Recorded rather than fixed, since this pass is documentation-only.

1. **`?search=` on health records is broken.**
   [`views.py:283`](../backend/clinic/views.py#L283) filters on
   `Q(consultations__consultation__icontains=search)`. `consultations` is a reverse relation on
   **Student**, not on HealthRecord — confirmed by introspecting the model, which reports
   `Cannot resolve keyword 'consultations' into field`. Any `GET /api/health-records/?search=<text>`
   raises `FieldError`. The correct path is `student__consultations__consultation`.
   No test covers this query parameter, which is why the suite still passes.

2. **`urlpatterns` is defined twice in `backend/config/urls.py`.** The first block (lines 26-32) is
   dead: Python keeps only the last assignment. The routes currently resolve from the second block,
   which includes the schema endpoints. Behaviour is correct today, but the duplicate is a latent
   trap — deleting the wrong block would silently drop `/api/schema/`.

3. **`ALLOWED_HOSTS` default is `'localhost,127.0.0.1,*'`.** The trailing wildcard makes the explicit
   host list decorative; `Host` header validation is effectively disabled outside production
   hardening.

4. **`.env.example` and `settings.py` disagree on CORS.** `.env.example` lists four origins including
   `:3000`; `settings.py` hardcodes only `http://localhost:5173` and `http://127.0.0.1:5173`. The
   `CORS_ALLOWED_ORIGINS` list in `settings.py` is a literal and is **not** read from the environment,
   so editing `.env` has no effect on CORS.

5. **`SECRET_KEY` has a hardcoded fallback** in `settings.py` that is identical to the value shipped
   in `.env.example`. The key is therefore not environment-only in practice.

6. **`StudentViewSet.get_queryset()` ignores non-numeric search.** `?search=abc` returns the
   **unfiltered** list rather than an empty one, because the filter is gated on
   `search.isdigit()` with no `else` branch (`views.py:101-104`).

7. **`main.py` is a PyCharm scratch script** printing `Hi, PyCharm`. It is unrelated to the system and
   the README describes it as a "standalone entry script".

### 6.4 Stale generated client

`gen/` is an openapi-generator 7.7.0 Python client generated **before** the Consultation split. It
contains `StudentsApi` and `HealthRecordsApi` only — no `ConsultationsApi`, no `HealthStatusesApi`,
and its `HealthRecord` model still carries `visit` and `consultation` fields. It does not match the
current schema and should be regenerated or removed.