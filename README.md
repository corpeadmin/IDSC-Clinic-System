# IDSC Clinic System

The **IDSC Clinic System** is the Clinic module of the class College Management System (CMS).

The backend manages Clinic-owned medical data and coordinates API-level integrations with Registrar, Inventory, Faculty, and Student Portal while preserving each module's domain ownership.

This README describes the verified backend baseline and the frontend integration on `integration/clinic-final`. See `docs/CONSOLIDATION-AUDIT.md` for branch selection and `docs/INTEGRATION-VALIDATION.md` for current validation.

---

## 1. Verified Project Baseline

| Item | Verified value |
|---|---|
| Business API namespace | `/api/v1/` |
| Authentication namespace | `/api/auth/` |
| Canonical health endpoint | `GET /api/v1/health` |
| Canonical health response | `{ "status": "ok" }` |
| Dynamic OpenAPI schema | `/api/schema/` |
| Canonical Swagger UI | `/docs` |
| ReDoc | `/api/schema/redoc/` |
| OpenAPI version | `3.1.0` |
| Documented API paths | `35` |
| Documented API operations | `53` |
| Public operations | `3` |
| Protected operations | `50` |
| Permanent Django tests | `257` |
| Permanent Django tests passed | `257` |
| Permanent Django tests failed | `0` |
| Original Postman requests | `45` |
| Original Newman requests executed | `45` |
| Newman assertions | `46` |
| Newman failures | `0` |

The canonical static API contract is `openapi.yaml`.

The canonical runtime Swagger UI is `/docs`. The older `/api/schema/swagger-ui/` route remains only as a backward-compatible runtime alias.

The canonical health operation is `/api/v1/health` without a trailing slash. A trailing-slash runtime alias may remain for compatibility, but it is intentionally excluded from the canonical OpenAPI operation inventory.

---

## 2. Midterm Architecture

For the midterm, Clinic business data uses mock/in-memory storage.

The active business-data flow is:

```text
HTTP route
   |
   v
DRF view/controller
   |
   v
ClinicService
   |
   v
MockClinicRepository
```

The views handle HTTP concerns and delegate Clinic business operations to `ClinicService`.

`ClinicService` handles domain rules and cross-module orchestration.

`MockClinicRepository` stores Clinic-owned business resources in memory for the midterm.

### Django framework database

Django still needs a database for framework infrastructure such as:

- authentication;
- groups and permissions;
- sessions;
- admin support.

The default framework database is SQLite.

This **does not mean Clinic business resources are persisted through Django ORM during the midterm**.

### Finals database direction

PostgreSQL remains available as an opt-in finals configuration.

Finals dependencies are separated in:

`backend/requirements-finals.txt`

A future database-backed Clinic repository can replace the mock repository without changing the public route structure.

---

## 3. Domain Ownership

### Registrar owns

- student identity;
- student profile;
- course and section;
- `student_id`.

Clinic consumes Registrar-owned student data through a Registrar integration boundary.

The current midterm implementation uses deterministic mock Registrar data.

### Clinic owns

- `HealthRecord`;
- `Consultation`;
- `HealthStatus`;
- `MedicineDispensation`.

Clinic also owns Clinic-specific reports and Clinic account-management behavior.

### Inventory owns

- medicine catalog;
- medicine stock;
- `medicine_id`;
- Inventory stock transactions.

Clinic consumes Inventory-owned medicine and stock information through an Inventory integration boundary.

The current midterm implementation uses deterministic in-memory Inventory data and transactions.

### Faculty and Student Portal

Clinic exposes restricted **read-only health-status projections** for:

- Faculty;
- Student Portal.

These consumers do not own or directly modify Clinic health-status persistence.

---

## 4. External Identifier Contract

Clinic references externally owned data using API-level identifiers:

- `student_id`;
- `medicine_id`;
- `inventory_transaction_id`;
- `rollback_transaction_id` when rollback/compensation occurs.

These are cross-module references, not shared-database foreign keys.

Registrar remains authoritative for student identity.

Inventory remains authoritative for medicine catalog and stock.

---

## 5. Integration Architecture

```text
                         +----------------------+
                         |      Registrar       |
                         | student identity     |
                         | student profile      |
                         +----------+-----------+
                                    |
                                    | student_id / validation
                                    v
+------------------+      +---------+----------+      +----------------------+
| Faculty          |<-----|                    |----->|      Inventory       |
| read-only health |      |       CLINIC       |      | medicine catalog     |
+------------------+      |                    |      | medicine stock       |
                          | HealthRecord       |      | stock transactions   |
+------------------+      | Consultation       |      +----------------------+
| Student Portal   |<-----| HealthStatus       |
| read-only health |      | Dispensation       |
+------------------+      +---------+----------+
                                    |
                                    v
                          ClinicService
                                    |
                                    v
                          MockClinicRepository
                          (midterm business data)
```

### Medicine-dispensation orchestration

Creating a medicine dispensation coordinates three boundaries:

1. validate the student through Registrar;
2. deduct medicine stock through Inventory;
3. persist the Clinic-owned dispensation through the Clinic repository.

If Clinic persistence fails after Inventory deduction, the service attempts a compensating stock restore.

Explicit dispensation rollback restores Inventory stock and records the Clinic-owned dispensation as rolled back.

See `docs/integration.md` for full sequence and error behavior.

---

## 6. Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- drf-spectacular
- django-cors-headers
- python-dotenv

### Midterm data/runtime infrastructure

- `MockClinicRepository` for Clinic business-domain data
- deterministic mock Registrar service
- deterministic mock Inventory service
- SQLite for Django framework infrastructure

### Finals opt-in

- PostgreSQL through environment configuration
- `psycopg` through `backend/requirements-finals.txt`

### Frontend repository

- React
- Vite
- JavaScript / JSX
- CSS

The frontend uses the clinic layout selectively recovered from the legacy UI branch and connects to the verified session-authenticated API. It supports student/medicine projections, health records, consultations, health statuses, dispensing/rollback, reports and administrator staff management. Business data remains in the verified mock backend; page reloads retain server state, backend restarts reset it.

See `docs/design-system.md` for the verified repository design baseline and Figma synchronization rules.

### API/testing tooling

- OpenAPI 3.1
- Swagger UI
- ReDoc
- Postman
- Newman
- Redocly CLI
- Git

---

## 7. Repository Structure

```text
IDSC-Clinic-System-Clean/
|
+-- backend/
|   +-- authentication/
|   +-- clinic/
|   |   +-- data/
|   |   +-- services/
|   |   +-- tests/
|   +-- config/
|   +-- manage.py
|   +-- requirements.txt
|   +-- requirements-finals.txt
|
+-- docs/
|   +-- architecture.md
|   +-- data-model.md
|   +-- integration.md
|   +-- design-system.md
|   +-- TEST-EVIDENCE.md
|   +-- decisions/
|       +-- 0001-midterm-mock-domain-data.md
|       +-- 0002-domain-ownership-and-external-identifiers.md
|       +-- 0003-service-repository-layering.md
|       +-- 0004-session-authentication-csrf-and-cors.md
|       +-- 0005-openapi-health-and-documentation-contract.md
|       +-- 0006-clean-integration-and-pr-only-main.md
|
+-- frontend/
|
+-- postman/
|   +-- IDSC-Clinic-System.postman_collection.json
|
+-- openapi.yaml
+-- redocly.yaml
+-- API.md
+-- SETUP.md
+-- README.md
```

---

## 8. Backend Configuration

Primary Django configuration:

`backend/config/settings.py`

Important verified configuration includes:

- `CLINIC_DATA_BACKEND` defaults to `mock`;
- default framework database is SQLite;
- PostgreSQL is opt-in through environment configuration;
- `ClinicSessionAuthentication` is the default DRF authentication class;
- `IsAuthenticated` is the default DRF permission;
- custom Problem Details exception handling is configured;
- CSRF middleware is enabled;
- credentialed CORS is explicitly configured;
- drf-spectacular generates the dynamic OpenAPI schema;
- project-level OpenAPI metadata is normalized through `config.schema.postprocess_openapi_metadata`.

---

## 9. Authentication and Authorization

The midterm backend uses Django session authentication.

Authentication routes include:

| Method | Endpoint | Access |
|---|---|---|
| `GET` | `/api/auth/csrf/` | Public |
| `POST` | `/api/auth/login/` | Public |
| `POST` | `/api/auth/logout/` | Authenticated |
| `GET` | `/api/auth/me/` | Authenticated |
| `POST` | `/api/auth/password/change/` | Authenticated |
| `POST` | `/api/auth/username/change/` | Authenticated |

The default authentication class is:

`authentication.authentication.ClinicSessionAuthentication`

The default REST permission is:

`rest_framework.permissions.IsAuthenticated`

Clinic role permissions include:

- `IsClinicStaff`;
- `IsClinicAdmin`.

Protected business endpoints require authentication and the appropriate role.

The Faculty and Student Portal integration projections require authentication but are not Clinic-staff write operations.

---

## 10. CSRF and CORS

Django's `CsrfViewMiddleware` remains enabled.

Unsafe session-authenticated requests require CSRF protection.

The frontend can obtain a CSRF token through:

`GET /api/auth/csrf/`

Credentialed CORS is enabled only for the approved local Vite origins:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

The same local origins are configured as trusted CSRF origins.

Do not disable CSRF or enable wildcard credentialed CORS to simplify frontend development.

---

## 11. Canonical API and Documentation Routes

| Purpose | Route |
|---|---|
| Backend discovery | `/` |
| Authentication | `/api/auth/` |
| Business API | `/api/v1/` |
| Dynamic OpenAPI | `/api/schema/` |
| Swagger UI | `/docs` |
| ReDoc | `/api/schema/redoc/` |
| Django Admin | `/admin/` |

### Health contract

Canonical request:

```http
GET /api/v1/health
```

Exact response:

```json
{
  "status": "ok"
}
```

The health operation is public.

---

## 12. API Endpoint Reference

The authoritative schemas, request bodies, response bodies, examples, and security metadata are defined in `openapi.yaml`.

The current contract contains **72 operations**.

### Authentication

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/auth/csrf/` | Public | Get CSRF token |
| `POST` | `/api/auth/login/` | Public | Log in |
| `POST` | `/api/auth/logout/` | Authenticated | Log out |
| `GET` | `/api/auth/me/` | Authenticated | Get current user |
| `POST` | `/api/auth/password/change/` | Authenticated | Change own password |
| `POST` | `/api/auth/username/change/` | Authenticated | Change own username |

### Health and dashboard

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | Public | Health check |
| `GET` | `/api/v1/dashboard/` | Clinic staff/admin | Dashboard summary |

### Registrar-backed student projection

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/students/` | Clinic staff/admin | List students |
| `GET` | `/api/v1/students/{student_id}/` | Clinic staff/admin | Get student |

### Health records

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/health-records/` | Clinic staff/admin | List |
| `POST` | `/api/v1/health-records/` | Clinic staff/admin | Create |
| `GET` | `/api/v1/health-records/{health_record_id}/` | Clinic staff/admin | Retrieve |
| `PUT` | `/api/v1/health-records/{health_record_id}/` | Clinic staff/admin | Replace |
| `PATCH` | `/api/v1/health-records/{health_record_id}/` | Clinic staff/admin | Partial update |
| `DELETE` | `/api/v1/health-records/{health_record_id}/` | Clinic staff/admin | Delete |

### Consultations

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/consultations/` | Clinic staff/admin | List |
| `POST` | `/api/v1/consultations/` | Clinic staff/admin | Create |
| `GET` | `/api/v1/consultations/{consultation_id}/` | Clinic staff/admin | Retrieve |
| `PUT` | `/api/v1/consultations/{consultation_id}/` | Clinic staff/admin | Replace |
| `PATCH` | `/api/v1/consultations/{consultation_id}/` | Clinic staff/admin | Partial update |
| `DELETE` | `/api/v1/consultations/{consultation_id}/` | Clinic staff/admin | Delete |

### Health statuses

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/health-statuses/` | Clinic staff/admin | List |
| `POST` | `/api/v1/health-statuses/` | Clinic staff/admin | Create |
| `GET` | `/api/v1/health-statuses/{status_id}/` | Clinic staff/admin | Retrieve |
| `PUT` | `/api/v1/health-statuses/{status_id}/` | Clinic staff/admin | Replace |
| `PATCH` | `/api/v1/health-statuses/{status_id}/` | Clinic staff/admin | Partial update |
| `DELETE` | `/api/v1/health-statuses/{status_id}/` | Clinic staff/admin | Delete |

### Inventory-backed medicine projection

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/medicines/` | Clinic staff/admin | List medicines |
| `GET` | `/api/v1/medicines/{medicine_id}/` | Clinic staff/admin | Get medicine |

### Medicine dispensations

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/medicine-dispensations/` | Clinic staff/admin | List |
| `POST` | `/api/v1/medicine-dispensations/` | Clinic staff/admin | Dispense medicine |
| `GET` | `/api/v1/medicine-dispensations/{dispensation_id}/` | Clinic staff/admin | Retrieve |
| `POST` | `/api/v1/medicine-dispensations/{dispensation_id}/rollback/` | Clinic staff/admin | Roll back |

### Reports

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/reports/clinic-visits/` | Clinic staff/admin | Clinic visit report |
| `GET` | `/api/v1/reports/health-records/` | Clinic staff/admin | Health-record report |
| `GET` | `/api/v1/reports/medicine-inventory/` | Clinic staff/admin | Inventory projection report |
| `GET` | `/api/v1/reports/medicine-dispensations/` | Clinic staff/admin | Dispensation report |

### External health-status projections

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/integrations/faculty/health-status/{student_id}/` | Authenticated | Faculty projection |
| `GET` | `/api/v1/integrations/student-portal/health-status/{student_id}/` | Authenticated | Student Portal projection |

### Clinic user management

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/users/` | Clinic admin | List accounts |
| `POST` | `/api/v1/users/` | Clinic admin | Create account |
| `GET` | `/api/v1/users/{user_id}/` | Clinic admin | Retrieve account |
| `PUT` | `/api/v1/users/{user_id}/` | Clinic admin | Replace account |
| `PATCH` | `/api/v1/users/{user_id}/` | Clinic admin | Partial update |
| `POST` | `/api/v1/users/{user_id}/activate/` | Clinic admin | Activate account |
| `POST` | `/api/v1/users/{user_id}/deactivate/` | Clinic admin | Deactivate account |

---

## 13. Problem Details and Validation

The API uses the project's Problem Details representation for standardized errors.

Canonical fields include:

- `type`;
- `title`;
- `status`;
- `detail`;
- `instance`;
- `code`.

Validated status categories include:

- `400 Bad Request`;
- `401 Unauthorized`;
- `403 Forbidden`;
- `404 Not Found`;
- `409 Conflict`;
- `422 Unprocessable Entity`.

Validation and integration errors are translated at the API boundary instead of exposing internal exceptions directly.

---

## 14. OpenAPI Contract

Static contract:

`openapi.yaml`

Dynamic schema:

`/api/schema/`

Canonical Swagger UI:

`/docs`

Redoc:

`/api/schema/redoc/`

The generated contract uses the canonical local server:

`http://127.0.0.1:8002`

The current verified operation inventory is:

- 43 paths;
- 70 operations;
- 3 public operations;
- 67 protected operations.

The three explicitly public operations are:

- `GET /api/v1/health`;
- `GET /api/auth/csrf/`;
- `POST /api/auth/login/`.

Static and dynamic operation inventories were verified to match.

Both static and dynamic contracts passed Redocly validation during the integration verification.

---

## 15. Automated Test and Postman Evidence

Canonical recorded evidence is in:

`docs/TEST-EVIDENCE.md`

Current baseline:

| Test area | Result |
|---|---:|
| Django tests discovered | 257 |
| Django tests passed | 257 |
| Django tests failed | 0 |
| Original Postman requests | 45 |
| Original Newman requests executed | 45 |
| Newman assertions | 46 |
| Newman failures | 0 |

The Postman collection is:

`postman/IDSC-Clinic-System.postman_collection.json`

Before final merge, the complete automated suite, OpenAPI validation, Redocly lint, runtime Swagger checks, Problem Details checks, and Postman/Newman verification must be run again.

---

## 16. Development Setup

The midterm does **not** require PostgreSQL to run Clinic business endpoints.

### Create/activate a Python environment

Use a project virtual environment appropriate for your operating system.

### Install midterm/backend dependencies

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
```

### Enter the backend project

```powershell
Set-Location backend
```

### Apply Django framework migrations

```powershell
python manage.py migrate
```

These migrations support Django framework infrastructure and retain finals-oriented domain migration history. They do not change the fact that the active midterm Clinic business-data backend is `mock`.

### Run Django checks

```powershell
python manage.py check
```

### Run the server

```powershell
python manage.py runserver 8002
```

Backend:

`http://127.0.0.1:8002/`

Swagger:

`http://127.0.0.1:8002/docs`

### Finals PostgreSQL dependencies

For finals-oriented PostgreSQL work:

```powershell
python -m pip install -r requirements-finals.txt
```

Use the documented database environment configuration only when intentionally switching to the finals database path.

See `SETUP.md` for additional environment/setup information, but treat this README and the architecture decision records as authoritative for the current midterm mock-data policy.

---

## 17. Frontend Status

The repository contains a React/Vite frontend scaffold.

The currently committed implementation still contains starter React/Vite content and does **not** represent the final Clinic high-fidelity interface.

The final frontend role requires the approved high-fidelity clickable Figma prototype and synchronized implementation.

The repository design evidence currently includes:

- CSS custom properties;
- system font stacks;
- system-driven light/dark values;
- a `1024px` responsive breakpoint;
- basic hover/focus-visible interaction styling.

Do not present these starter styles as the completed Clinic design system.

See:

`docs/design-system.md`

---

## 18. Architecture Documentation

Detailed documentation is maintained under `docs/`.

### Core documents

- [`docs/architecture.md`](docs/architecture.md) — backend boundaries, layering, runtime architecture, and midterm/finals separation.
- [`docs/data-model.md`](docs/data-model.md) — Clinic resource definitions, identifiers, choices, and external references.
- [`docs/integration.md`](docs/integration.md) — Registrar, Inventory, Faculty, Student Portal, compensation, rollback, and trust boundaries.
- [`docs/design-system.md`](docs/design-system.md) — verified frontend styling evidence and Figma synchronization contract.
- [`docs/TEST-EVIDENCE.md`](docs/TEST-EVIDENCE.md) — recorded automated/API validation evidence.

### Architecture Decision Records

- [`ADR 0001`](docs/decisions/0001-midterm-mock-domain-data.md) — mock in-memory Clinic domain data for the midterm.
- [`ADR 0002`](docs/decisions/0002-domain-ownership-and-external-identifiers.md) — module ownership and external identifiers.
- [`ADR 0003`](docs/decisions/0003-service-repository-layering.md) — routes/views to services to data-layer architecture.
- [`ADR 0004`](docs/decisions/0004-session-authentication-csrf-and-cors.md) — session authentication, CSRF, and credentialed CORS.
- [`ADR 0005`](docs/decisions/0005-openapi-health-and-documentation-contract.md) — canonical OpenAPI, health, and Swagger contracts.
- [`ADR 0006`](docs/decisions/0006-clean-integration-and-pr-only-main.md) — clean Phase 7-based integration and PR-only `main`.

---

## 19. Git and Integration Rules

The canonical source branch to preserve is:

`phase7/tests-contract-validation`

The clean integration branch is:

`fix/pre-main-integration`

Rules:

1. Do not merge legacy feature branches wholesale into `main`.
2. Do not push directly to `main`.
3. Do not force-push the integration branch as part of normal workflow.
4. Preserve meaningful commit history.
5. Review staged content before committing.
6. Merge to `main` only through a reviewed Pull Request.
7. Require final validation gates before merge.
8. Preserve canonical Phase 7 until the reviewed integration is complete.

Legacy feature branches are historical/reference branches according to the integration baseline and should not be treated as current canonical implementations.

---

## 20. Final Merge Gates

Before the integration Pull Request can merge to `main`, verify all of the following:

- [ ] full Django automated tests pass;
- [ ] `python manage.py check` passes;
- [ ] migration drift check passes;
- [ ] static OpenAPI validates;
- [ ] dynamic OpenAPI generates and validates;
- [ ] static/dynamic operation inventory matches;
- [ ] Redocly static lint passes;
- [ ] Redocly dynamic lint passes;
- [ ] `/api/v1/health` returns exactly `{ "status": "ok" }`;
- [ ] Swagger `/docs` works;
- [ ] Problem Details behavior is verified;
- [ ] Postman/Newman collection is verified;
- [ ] documentation is synchronized;
- [ ] `main` branch protection is enabled as required;
- [ ] teammate PR approval is obtained.

---

## 21. Security and Data Integrity Rules

- Do not commit real passwords or production credentials.
- Do not commit local virtual environments.
- Do not commit generated Python cache/bytecode.
- Keep session authentication enabled for protected browser flows.
- Keep CSRF protection enabled.
- Keep credentialed CORS restricted to intentional origins.
- Keep public operations explicitly public rather than weakening global permissions.
- Preserve module domain ownership.
- Do not treat external identifiers as shared-database ownership.
- Do not bypass `ClinicService` to persist Clinic business data directly from views.

---

## 22. Current Documentation Status

The previously missing integration documentation set is now present in the working integration documentation sequence:

- `docs/architecture.md`;
- `docs/data-model.md`;
- `docs/integration.md`;
- `docs/design-system.md`;
- `docs/decisions/`.

These files must be validated and committed together only after README synchronization and documentation-quality checks pass.

---

## 23. Source-of-Truth Files

Primary implementation/contract sources:

- `openapi.yaml`
- `redocly.yaml`
- `backend/config/settings.py`
- `backend/config/urls.py`
- `backend/config/schema.py`
- `backend/clinic/urls.py`
- `backend/clinic/views.py`
- `backend/clinic/services/clinic.py`
- `backend/clinic/services/registrar.py`
- `backend/clinic/services/inventory.py`
- `backend/clinic/data/clinic.py`
- `backend/authentication/`
- `docs/TEST-EVIDENCE.md`

Primary architecture documentation:

- `docs/architecture.md`
- `docs/data-model.md`
- `docs/integration.md`
- `docs/design-system.md`
- `docs/decisions/`

When implementation, API contract, test evidence, or approved frontend design changes materially, synchronize the relevant documentation in the same reviewed workflow.


## Self-service password change

`POST /api/auth/password/change/` accepts `current_password`, `new_password`, and `confirm_password`. It requires the current session and a fresh `X-CSRFToken`, verifies the current password, requires a different matching new password, and applies configured Django password validators. Password strings are not trimmed and are limited to 1024 characters. Success returns only `{ "message": "Your password has been changed." }`. The current session is rotated and retained; other sessions expire on their next request. Validation errors use HTTP 400 Problem Details with field errors.

Open Settings > Change password to use the flow. See `docs/PASSWORD-CHANGE.md` for details. All 45 pre-existing operations are preserved; the current schema has 45 paths and 72 operations. The original Postman collection remains a 45-request regression suite; the isolated password-change collection adds its own flow.


## Username and administrator management

`POST /api/auth/username/change/` changes only the signed-in user's username after current-password verification. It accepts `new_username` and `current_password`; names are validated, trimmed, Unicode-normalized and checked for duplicates. The current session remains signed in and the response contains updated account information.

`GET /api/v1/admins/` lists administrators and `POST /api/v1/admins/` creates an additional Clinic administrator. Both require existing Clinic administrator permission. Creation accepts `username`, `password`, `confirm_password`, the acting administrator's `current_password`, and optional `first_name`, `last_name`, `email`. Strong password validation applies. The new account receives `CLINIC_ADMIN`, never Django superuser privileges. Staff cannot create or list administrators. All writes require CSRF.

Use Settings > Change username or Administration > Add administrator. See `docs/ACCOUNT-MANAGEMENT.md`. The schema contains 45 paths and 72 operations (5 public, 67 protected); every original API definition remains unchanged.


## Account deactivation and deletion

Administration now provides Deactivate/Activate and Delete for both administrator and staff accounts. New operations: `DELETE /api/v1/admins/{user_id}/`, `POST /api/v1/admins/{user_id}/deactivate/`, `POST /api/v1/admins/{user_id}/activate/`, and `DELETE /api/v1/users/{user_id}/`. Permanent deletion requires JSON `{ "current_password": "your current password" }` and CSRF. Successful deletion returns HTTP 204 with no body.

Only an active Clinic administrator can perform account lifecycle changes. Self-removal and last-active-admin removal are blocked. System administrators can be managed only by another system administrator, and admin accounts cannot be managed through staff lifecycle routes. Deactivation revokes existing database sessions; reactivation requires a fresh login. Deletion preserves clinic medical records. Admin directory rows include `is_system_admin`, `can_manage`, and `management_restriction` for UI hints; backend checks remain authoritative. See `docs/ACCOUNT-LIFECYCLE.md`.


## Owner, Admin and Staff

Owner manages Admins and Staff; Admin manages Staff only; Staff uses clinic features without account management. Owner accounts are protected from deletion/deactivation. Existing Django superusers are Owners; clinic groups retain their current Admin/Staff roles. Session responses expose the role. Admin account detail now supports GET/PUT/PATCH as well as DELETE, and account edits support validated usernames. See [ROLE-HIERARCHY.md](docs/ROLE-HIERARCHY.md) for the permission matrix and API details. This policy supersedes earlier descriptions allowing Admins to manage Admins.


## Staff pages and Admin capacity

Staff management now shows ten accounts per page with working Previous/Next controls and search-aware page counts. `GET /api/v1/users/` returns the Clinic pagination envelope, default/max `page_size=10`. Admin creation has a server-enforced five-account maximum, including inactive Admins and excluding Owners; capacity returns 409 until an Admin is deleted. See [ACCOUNT-LIMITS.md](docs/ACCOUNT-LIMITS.md) for details and validation fixtures.


## Registrar and Inventory demo workflows

Consecutive visible record labels, Owner/Admin-only clinical/history deletion, Get student by Registrar ID, automatic profile/status updates, Owner-operated Mock Registrar/Inventory workspaces, medicine notifications and selected/all restock requests with Inventory fulfillment are now connected to backend APIs. Internal record IDs stay stable; deleting dispensing history never reverses stock. These mock data reset on backend restart. See [EXTERNAL-WORKFLOWS.md](docs/EXTERNAL-WORKFLOWS.md) for roles, routes, examples and demonstration limits. Current inventory: 43 paths / 70 operations.


## First-time Owner registration

Run migrations, then open the website. A fresh installation shows Owner registration, creates exactly one Owner, and opens Dashboard automatically. Logout and later visits show the shared Owner/Admin/Staff login. Existing installations keep their Owner; registration remains closed. See [OWNER-REGISTRATION.md](docs/OWNER-REGISTRATION.md) for API details, migration behavior and validation.
