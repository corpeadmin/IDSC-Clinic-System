# ADR-0001: Backend framework — Django 6.1 with Django REST Framework

- **Status:** Accepted
- **Date:** 2026-08-18 — date of the initial commit, which first added `backend/config/settings.py`
- **Deciders:** IDSC Clinic System team

---

## Context

The IDSC Clinic System needs a backend that:

1. Persists student health records, consultations, and health status in a relational database with
   real foreign keys and referential integrity.
2. Serves several **external** consumers over HTTP — a Student Portal System (read-only), a Faculty
   System (CRUD), and a frontend SPA — all of which need a stable, machine-readable contract.
3. Exposes a staff back-office for clinic personnel to view and amend records.
4. Enforces input validation on clinical values (weight, height, blood type) and prevents raw database
   errors from leaking to clients.
5. Is maintainable by a small student team without dedicated DevOps infrastructure.

The central question was which server-side framework to build on.

---

## Decision

**Use Django 6.1 with Django REST Framework (DRF) 3.18, backed by PostgreSQL.**

The concrete adoption:

| Choice | Detail | Evidence |
| :--- | :--- | :--- |
| Framework | Django 6.1 (`Django>=6.1,<6.2`) | `backend/requirements.txt:1` |
| REST layer | Django REST Framework 3.18 | `requirements.txt:2` |
| Database | PostgreSQL via `psycopg[binary]` 3.3.4 | `requirements.txt:4` |
| API schema | drf-spectacular ≥ 0.30 | `requirements.txt:6` |
| CORS | django-cors-headers ≥ 4.9 | `requirements.txt:3` |
| Configuration | python-dotenv ≥ 1.2.3 | `requirements.txt:5` |

Architecture follows Django conventions rather than a custom layout: a `config` project package
holding settings and root URLs, and two apps — `clinic` (the domain) and `authentication` (session
auth views).

---

## Rationale

### Why Django

**The Django admin satisfied requirement 3 with almost no code.** This is the decisive factor for a
small team. `django.contrib.admin` is part of the framework, so the clinic gained a working staff
interface — searchable students, filtered records, tabular inlines for health records and
consultations on the student page — from roughly 150 lines of configuration in
`backend/clinic/admin.py`. A leaner framework would have required building that interface from
scratch. As of this ADR, **Django Admin is the only working user interface in the project.**

**Migrations solved the schema problem.** Requirement 1 is met by `python manage.py makemigrations` /
`migrate`, giving a versioned, reversible schema history — including the data migration in
`0005_consultation.py` that copied `visit` and `consultation` out of `health_records` before dropping
those columns. `SETUP.md` states the rule explicitly: developers never create tables with raw SQL.

**The ORM covers requirement 4's integrity concerns directly.** Foreign keys with `on_delete=CASCADE`,
index declarations, `DecimalField(5, 2)` for vitals, and `TextChoices` for blood type are declarative.
Queries are parameterised by construction, so SQL injection is not a class of bug the team has to
avoid by discipline.

**DRF solved requirement 2 cheaply.** `DefaultRouter` plus `ModelViewSet` produced the full REST
surface for four models with no hand-written view code, and `ReadOnlyModelViewSet` gave the Student
Portal its read-only boundary as a base-class choice rather than a permission list. DRF's serializer
validation maps cleanly onto requirement 4: `validate_weight`, `validate_height`, and
`validate_blood_type` are ordinary methods.

**drf-spectacular closed the contract loop.** The machine-readable schema is generated from the code
itself, so `openapi.json` and `openapi.yaml` cannot drift from the implementation the way hand-written
API documents do. This is what allows the generated Python client under `gen/` and the external
integrations to be specified against a single source of truth.

### Why not the alternatives

| Option | Why not |
| :--- | :--- |
| **Flask** | No ORM, no migrations, no admin. Each of the three would need a separate third-party dependency and integration work — a large tax for a small team, and the admin alone would have to be hand-built. |
| **FastAPI** | Excellent typing and native OpenAPI generation, and a legitimate choice on those grounds. Against it: no built-in admin, so requirement 3 becomes a separate build; and its async-first model adds complexity that buys nothing here, since the workload is a small number of relational CRUD endpoints with no concurrency pressure. The Pydantic-based validation would also have been re-implemented alongside ORM field constraints. |
| **Node/Express** | Would have unified the stack with the React frontend. Against it: the ORM and migration story is materially weaker than Django's for a schema with four related entities and cascade semantics, and no admin. |
| **Django + FastAPI hybrid** | Two routers, two validation systems, two sets of dependencies. Indefensible at this size. |

### Why PostgreSQL

Chosen over SQLite and MySQL. PostgreSQL gives enforced foreign keys with `ON DELETE CASCADE`,
`DecimalField` precision for vitals, and `BigIntegerField` for externally supplied IDs up to 2^63-1.
SQLite would not enforce foreign keys by default, which undermines the one guarantee the data model
depends on. The database runs in a `clinic-postgres` Docker container on `16-alpine` for reproducible
local environments.

---

## Consequences

### Positive

- Full CRUD API for four entities implemented in a small, conventional codebase
- A working staff UI via Django Admin, available immediately
- Reversible, versioned schema migrations including data movement
- Generated OpenAPI schema that cannot silently drift from the code
- Uniform error envelope via a single custom DRF exception handler

### Negative / accepted costs

- **Django's convention-heavy structure** adds ceremony for a small service; the `config` + app split
  is more structure than a minimal API would need.
- **Synchronous ORM under WSGI/ASGI.** Fine for this workload, but it is a ceiling if the system later
  needs high-concurrency fan-out.
- **Admin-first thinking.** Django encourages server-rendered CRUD, which is not the target UX. The
  frontend must supply the real interface.
- **Django 6.1 is recent**, so long-term support stability is less proven than a mature major version.

### Follow-on decisions

- Splitting consultations out of health records — [ADR-0002](0002-split-consultations-from-health-records.md)
- Externally supplied `student_id` as the primary key — [ADR-0003](0003-externally-supplied-student-id.md)

---

## Notes on the current implementation

Recorded for accuracy, since they qualify the decision above. None of these are reasons to revisit
the framework choice.

- Global permissions are `AllowAny`, so the session-authentication app exists but is not enforced by
  any clinic viewset. See [integration.md §5](../integration.md#5-authentication-and-trust-boundaries).
- `ALLOWED_HOSTS` defaults to include a `*` wildcard.
- `backend/config/urls.py` assigns `urlpatterns` twice; only the second assignment is live.