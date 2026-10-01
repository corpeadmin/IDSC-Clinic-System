# Data Model

Source of truth: [`backend/clinic/models.py`](../backend/clinic/models.py) and the migration chain
in [`backend/clinic/migrations/`](../backend/clinic/migrations). Field types and constraints below
are read directly from the model definitions; the ER diagram is checked against the migrations that
actually applied.

Related documents: [architecture.md](architecture.md) · [integration.md](integration.md)

---

## 1. Entity Overview

Four domain entities, all owned by the `clinic` Django app:

| Model | Table | Primary key | Purpose |
| :--- | :--- | :--- | :--- |
| `Student` | `students` | `student_id` (`BigIntegerField`, externally supplied) | Identity anchor for all clinical data |
| `HealthRecord` | `health_records` | `health_id` (`BigAutoField`) | Standing medical attributes and physical vitals |
| `Consultation` | `consultations` | `consultation_id` (`BigAutoField`) | Per-visit notes and visit timestamps |
| `HealthStatus` | `health_statuses` | `status_id` (`BigAutoField`) | Health status reported by the Faculty System |

Plus the standard Django framework tables created by `migrate` (`auth_*`, `django_admin_log`,
`django_content_type`, `django_migrations`, `django_session`).

---

## 2. ER Diagram

```text
                    ┌──────────────────────────────┐
                    │         Student              │
                    │  PK  student_id  BigInteger  │  ← externally supplied
                    │      created_at              │    (never auto-generated)
                    │      updated_at              │
                    │      ordering: student_id    │
                    └───────┬───────────┬──────────┘
                            │           │
          ┌─────────────────┘           └─────────────────┐
          │ 1:N  on_delete=CASCADE                       │ 1:N  on_delete=CASCADE
          │ related_name='health_records'               │ related_name='consultations'
          │ related_name='health_statuses'              │
          ▼                                               ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│       HealthRecord           │        │        Consultation          │
│ PK  health_id   BigAuto      │        │ PK  consultation_id BigAuto  │
│ FK  student_id  → Student    │        │ FK  student_id    → Student  │
│     allergies    Text        │        │     consultation  Text       │
│     blood_type   Char(10)    │        │     visits       DateTime    │
│     medical_history Text     │        │     created_at   DateTime    │
│     medication   Text        │        │     updated_at   DateTime    │
│     weight       Dec(5,2)    │        │ ordering: -visits,           │
│     height       Dec(5,2)    │        │           -consultation_id   │
│     created_at / updated_at  │        │ idx_c_student_visit          │
│ ordering: -health_id         │        │ idx_c_visit                  │
│ idx_hr_student_id            │        └──────────────────────────────┘
└──────────────────────────────┘
          ┌──────────────────────────────┐
          │       HealthStatus           │
          │ PK  status_id   BigAuto      │
          │ FK  student_id  → Student    │
          │     health_status Text       │
          │     date        DateTime     │
          │     created_at / updated_at  │
          │ ordering: -date, -status_id  │
          │ idx_hs_student_date          │
          │ idx_hs_date                  │
          └──────────────────────────────┘
```

All three child tables hang off `Student`. `HealthRecord` and `Consultation` are **siblings, not
parent/child** — they were deliberately separated so that multiple consultations can exist per
student without duplicating the standing medical data. See
[ADR-0002](decisions/0002-split-consultations-from-health-records.md).

---

## 3. Entity Definitions

### 3.1 Student

`backend/clinic/models.py:25`

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | `BigIntegerField` | `primary_key=True` | Externally supplied unique identifier. Must be provided by the caller; the database does not generate it. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Last-updated timestamp. |

Metadata: table `students`, `ordering = ['student_id']`, **no indexes**.

`Student` holds no name, course, or contact fields. Migration `0003` removed the earlier
`student_name` / index / first-name / last-name columns and reduced the model to identity plus
timestamps, because names are owned by the Registrar.

### 3.2 HealthRecord

`backend/clinic/models.py:53`

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `health_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing record ID. |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='health_records'` | Owning student. |
| `allergies` | `TextField` | `blank=True, default=''` | Known medical, food, or environmental allergies. |
| `blood_type` | `CharField(max_length=10)` | `choices=BloodTypeChoices`, `blank=True, default=''` | Blood group; one of `A+ A- B+ B- AB+ AB- O+ O- Unknown`. |
| `medical_history` | `TextField` | `blank=True, default=''` | Chronic or past conditions. |
| `medication` | `TextField` | `blank=True, default=''` | Current medications. |
| `weight` | `DecimalField(5, 2)` | `null=True, blank=True`, validators `Min 0.0` / `Max 500.0` | Kilograms. |
| `height` | `DecimalField(5, 2)` | `null=True, blank=True`, validators `Min 0.0` / `Max 300.0` | Centimetres. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Last-updated timestamp. |

Metadata: table `health_records`, `ordering = ['-health_id']`, index `idx_hr_student_id` on
`(student, -health_id)`.

> **This table no longer has `visit` or `consultation` columns.** Both were moved to the
> `consultations` table by migration `0005_consultation.py`. Any documentation, client, or mock data
> still showing `visit` / `consultation` on a health record is out of date.

### 3.3 Consultation

`backend/clinic/models.py:130`

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `consultation_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing consultation ID. |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='consultations'` | Student the consultation belongs to. |
| `consultation` | `TextField` | `blank=True, default=''` | Notes, diagnosis, treatment. |
| `visits` | `DateTimeField` | `default=timezone.now` | Date and time of the clinic visit. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Last-updated timestamp. |

Metadata: table `consultations`, `ordering = ['-visits', '-consultation_id']`, indexes
`idx_c_student_visit` on `(student, -visits)` and `idx_c_visit` on `(-visits)`.

Note the field name is **`visits`** (plural) and is a `DateTimeField`.

### 3.4 HealthStatus

`backend/clinic/models.py:179`

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `status_id` | `BigAutoField` | `primary_key=True` | Auto-incrementing status ID. |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='health_statuses'` | Student the status belongs to. |
| `health_status` | `TextField` | `blank=True, default=''` | Reported health status detail. |
| `date` | `DateTimeField` | `default=timezone.now` | When the status was recorded. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Last-updated timestamp. |

Metadata: table `health_statuses`, `ordering = ['-date', '-status_id']`, indexes
`idx_hs_student_date` on `(student, -date)` and `idx_hs_date` on `(-date)`.

`health_status` is free text, not an enum — unlike `blood_type`, which is a validated
`TextChoices` set.

---

## 4. Relationships and Deletion Semantics

| Relationship | Cardinality | FK column | On delete |
| :--- | :--- | :--- | :--- |
| `Student` → `HealthRecord` | 1:N | `health_records.student_id` | `CASCADE` |
| `Student` → `Consultation` | 1:N | `consultations.student_id` | `CASCADE` |
| `Student` → `HealthStatus` | 1:N | `health_statuses.student_id` | `CASCADE` |

Deleting a student removes all health records, consultations, and health statuses in the same
operation. This is asserted by three model tests
(`test_cascade_delete_student_deletes_records`, `..._consultations`, `..._statuses`).

Note the FK `db_column` is `student_id` on all three child tables, matching the parent PK column
name, so the foreign key and the primary key share a column name across tables.

---

## 5. Index Strategy

| Index | Table | Columns | Purpose |
| :--- | :--- | :--- | :--- |
| `idx_hr_student_id` | `health_records` | `(student_id, -health_id)` | Per-student record listing, newest first |
| `idx_c_student_visit` | `consultations` | `(student_id, -visits)` | Per-student visit history, newest first |
| `idx_c_visit` | `consultations` | `(-visits)` | Global recency ordering |
| `idx_hs_student_date` | `health_statuses` | `(student_id, -date)` | Per-student status history |
| `idx_hs_date` | `health_statuses` | `(-date)` | Global recency ordering |

Every index pairs the FK with the model's `ordering` key, so the default list queries for a single
student are index-covered. `students` has no secondary index — its PK is sufficient given it is
searched by primary key.

Migration `0005` removed the earlier `idx_hr_student_visit` and `idx_hr_visit` indexes from
`health_records` when `visit` moved to `consultations`.

---

## 6. Migration History

| Migration | Change |
| :--- | :--- |
| `0001_initial.py` | Created `students` and `health_records` with FKs, checks, and indexes. |
| `0002_alter_student_student_id.py` | Set `Student.student_id` to an auto-incrementing `BigAutoField`. |
| `0003_remove_student_idx_student_name_and_more.py` | Reduced `Student` to `student_id` + timestamps; removed name columns and obsolete indexes; reverted `student_id` to a manually supplied `BigIntegerField`. |
| `0004_healthstatus.py` | Created `health_statuses` with FK and indexes. |
| `0005_consultation.py` | Created `consultations`; **data migration** copied `health_records.visit` and `.consultation` into it (`RunPython` with a reverse function); then dropped both columns from `health_records` and swapped the health-record indexes. |

`0005` is reversible: `reverse_move_consultations_to_health_records` writes the most recent
consultation back onto each student's highest-numbered health record. Note this reverse is lossy when
a student has several consultations — they cannot all be restored to a single record.

Migrations 0001 → 0005 were confirmed to apply cleanly against a fresh test database.

---

## 7. Model ↔ API Alignment

Field-level contract as served by the serializers in
[`backend/clinic/serializers.py`](../backend/clinic/serializers.py):

| Model | Serializer | Exposed fields |
| :--- | :--- | :--- |
| `Student` | `StudentSerializer` | `student_id`, `health_records_count` (computed), `consultations_count` (computed), `created_at`, `updated_at` |
| `Student` | `StudentDetailSerializer` | the above **plus** nested `health_records[]` and `consultations[]` |
| `HealthRecord` | `HealthRecordSerializer` | `health_id`, `student_id`, `allergies`, `blood_type`, `medical_history`, `medication`, `weight`, `height`, `created_at`, `updated_at` |
| `Consultation` | `ConsultationSerializer` | `consultation_id`, `student_id`, `consultation`, `visits`, `created_at`, `updated_at` |
| `HealthStatus` | `HealthStatusSerializer` | `status_id`, `student_id`, `health_status`, `date`, `created_at`, `updated_at` |

The model attribute `student` is serialised under the name **`student_id`** in every child
serializer, via `PrimaryKeyRelatedField(source='student')`. This is a deliberate naming choice so
the wire format matches the database column name rather than Django's default `student`.

`GET /api/students/{student_id}/` returns `StudentDetailSerializer`, so it nests both collections.
All other student endpoints return the flat `StudentSerializer`.

---

## 8. Validation Rules

Enforced in the serializers; violations return `400` through the shared error envelope.

| Field | Rule | Source |
| :--- | :--- | :--- |
| `student_id` (all children) | Must reference an existing `Student` | `serializers.py:17`, `:69`, `:94` |
| `blood_type` | Must be one of the nine `BloodTypeChoices` values | `serializers.py:55` |
| `weight` | `> 0` and `<= 500` kg | `serializers.py:39` |
| `height` | `> 0` and `<= 300` cm | `serializers.py:47` |
| `student_id` (Student) | Required on create; duplicates rejected as `400` | model PK + `IntegrityError` mapping |
| `health_id`, `consultation_id`, `status_id` | Read-only | `read_only_fields` |
| `created_at`, `updated_at` | Read-only, server-managed | `auto_now_add` / `auto_now` |

`HealthStatus.health_status` is not validated against any controlled vocabulary — any text is
accepted.

---

## 9. Mock Data / Generated Client Drift

`gen/` is an openapi-generator 7.7.0 Python client. It is **stale relative to the current schema**:

| Aspect | `gen/` client | Current API |
| :--- | :--- | :--- |
| API classes | `StudentsApi`, `HealthRecordsApi` | plus `ConsultationsApi`, `HealthStatusesApi` |
| `HealthRecord` fields | includes `visit`, `consultation` | both removed |
| `Consultation` model | absent | present |
| `HealthStatus` model | absent | present |

Do not treat `gen/` as mock data for the current contract. `openapi.json` / `openapi.yaml` at the
repository root are current; regenerate `gen/` from them if it is needed.