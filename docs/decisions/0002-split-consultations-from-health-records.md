# ADR-0002: Split consultations into their own table

- **Status:** Accepted
- **Date:** 2026-09-22
- **Deciders:** IDSC Clinic System team
- **Migration:** `backend/clinic/migrations/0005_consultation.py`
- **Supersedes:** the original `HealthRecord` schema, where `visit` and `consultation` were columns

---

## Context

Originally, `HealthRecord` carried both the standing medical attributes of a student and the record
of each clinic visit:

```text
health_records
  health_id, student_id
  allergies, blood_type, medical_history, medication, weight, height   ← standing data
  visit, consultation                                                    ← per-visit data
```

This conflated two different things with different cardinalities:

- **Standing data** — allergies, blood type, medical history, medication, current weight and height.
  A student has one current value for each. These do not meaningfully change per visit.
- **Per-visit data** — the date of the visit and the notes written during it. A student accumulates an
  unbounded number of these over time.

The two also have different shapes. Vitals are naturally re-measured per visit and read as a trend;
allergies and blood type are effectively static. Bundling them meant that logging a new consultation
either duplicated the standing data into a new row or overwrote it — both wrong.

The consequence showed up in the API: `GET /api/students/{student_id}/` nested a single
`health_records[]` array, which conflated "the student's medical file" with "the student's visit
history" and made a chronological visit timeline impossible to express.

---

## Decision

**Create a separate `Consultation` model that owns visit dates and notes, related to `Student` by
foreign key, and remove `visit` and `consultation` from `HealthRecord`.**

Resulting shape:

```text
students ──1:N──▶ health_records   (standing medical data)
        ──1:N──▶ consultations     (per-visit notes + timestamps)
        ──1:N──▶ health_statuses   (reported status)
```

`HealthRecord` and `Consultation` are siblings — both hang off `Student`, neither references the
other.

The new table:

| Field | Type | Notes |
| :--- | :--- | :--- |
| `consultation_id` | `BigAutoField` | PK, auto-increment |
| `student` | `ForeignKey(Student)` | `on_delete=CASCADE`, `db_column='student_id'`, `related_name='consultations'` |
| `consultation` | `TextField` | Notes, diagnosis, treatment |
| `visits` | `DateTimeField` | Visit timestamp, `default=timezone.now` |
| `created_at` / `updated_at` | `DateTimeField` | Audit timestamps |

Ordering `['-visits', '-consultation_id']`, with indexes `idx_c_student_visit` on `(student, -visits)`
and `idx_c_visit` on `(-visits)`.

`HealthRecord` ordering changed to `['-health_id']`, and its index changed from
`(student_id, -visit)` to `(student_id, -health_id)` — the visit-based index moved with the data.

Migration `0005` performs the move in a safe order: create the new table, add the indexes, run a
`RunPython` data migration copying every existing `visit` / `consultation` pair into a
`Consultation`, then remove the two columns from `health_records`. The reverse function writes the
most recent consultation back onto each student's highest-numbered health record.

The migration is reversible but **lossy in reverse** — a student with several consultations cannot
have them all restored to a single record.

---

## Rationale

**Correct cardinality.** A student now has one health record and an unbounded number of
consultations, which matches reality. Writing a visit note no longer touches the medical file.

**Chronological history became expressible.** `GET /api/students/{student_id}/consultations/`,
ordered `-visits`, is a genuine visit timeline. Previously no query could return it.

**Indexes moved with their data.** `idx_c_student_visit` and `idx_c_visit` now serve the recency
queries they were built for, instead of being attached to a table that no longer stores visit dates.

**Vitals trends became possible.** Because weight and height stay on `HealthRecord` and are no longer
overwritten by each visit, a series of health records per student can be read as a weight trend.

**The API mirrors the domain.** `StudentDetailSerializer` nests `health_records[]` and
`consultations[]` separately (`serializers.py:143-144`), so the distinction is visible in the response.

---

## Consequences

### Positive

- Visit history is a first-class, queryable, indexed resource
- Standing medical data is written once instead of duplicated per visit
- `StudentDetailSerializer` returns two clearly separated collections
- Three dedicated endpoints for consultations: list, detail CRUD, and nested per-student

### Negative / accepted costs

- **A breaking API change.** Health-record payloads lost `visit` and `consultation`. Any existing
  consumer must be updated.
- **One more join for "everything about a student."** Reconstructing a combined view now spans two
  tables.
- **Lossy reverse migration.** Rolling back `0005` cannot restore multiple consultations per student.
- **A code defect was introduced with the change.** `HealthRecordViewSet.get_queryset()` filters on
  `Q(consultations__consultation__icontains=search)` (`views.py:283`). `consultations` is a reverse
  relation on `Student`, not on `HealthRecord`, so any `GET /api/health-records/?search=<text>` raises
  `FieldError`. No test exercises this query parameter. The correct path is
  `student__consultations__consultation`. **This is an open bug** — see
  [architecture.md §6.3](../architecture.md#63-known-defects-found-while-verifying-this-document).
- **The generated client under `gen/` is stale.** It predates this split and its `HealthRecord` model
  still carries `visit` and `consultation`. Regenerate or remove it.

### Open integration question

The Student Portal consumes health records through
`GET /api/student-portal/health-records/`. That endpoint returns `HealthRecordSerializer`, which no
longer includes consultation notes. If the portal needs visit history, it must be given access to the
consultations endpoints — this has not been decided. Tracked as **AG-09** in
[integration.md §7](../integration.md#7-agreements-log).

---

## Follow-on

- None. [ADR-0003](0003-externally-supplied-student-id.md) concerns the identity key and is
  independent of this decision.