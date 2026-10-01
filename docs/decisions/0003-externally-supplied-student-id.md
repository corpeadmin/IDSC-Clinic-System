# ADR-0003: Externally supplied `student_id` as the primary key

- **Status:** Accepted
- **Date:** 2026-08-22 (`0002_alter_student_student_id`), completed 2026-09-06 (`0003_remove_student_idx_student_name_and_more`)
- **Deciders:** IDSC Clinic System team
- **Migration history:** `0001_initial` → `0002_alter_student_student_id` → `0003_remove_student_idx_student_name_and_more`

---

## Context

The clinic system does not own student identity. Student names, courses, and enrolment data belong to
the university's **Registrar**, which already issues a student number to every enrolled student.

Two designs were possible:

**Option A — surrogate key.** A local `id` as primary key, with the Registrar's student number stored
in a separate column, ideally with a uniqueness constraint.

**Option B — natural key.** The Registrar's student number is the primary key.

The migration history shows this decision was reversed once before reaching its current form:

- `0001_initial` created the table
- `0002_alter_student_student_id` set `student_id` to an auto-incrementing `BigAutoField`
- `0003_remove_student_idx_student_name_and_more` reverted `student_id` to a **manually supplied**
  `BigIntegerField` and deleted the name columns and their indexes

The project landed on Option B.

---

## Decision

**`Student.student_id` is a `BigIntegerField` declared `primary_key=True`, and the value is supplied
by the caller on creation. The database never generates it.**

```python
class Student(models.Model):
    student_id = models.BigIntegerField(
        primary_key=True,
        help_text="Externally supplied unique student identifier",
    )
```

`Student` holds only `student_id`, `created_at`, and `updated_at`. No name, course, or contact
fields — those belong to the Registrar.

All three child tables reference it by foreign key, and each FK column is also named `student_id`:

```text
students.student_id            (PK, supplied externally)
health_records.student_id      (FK, on_delete=CASCADE)
consultations.student_id       (FK, on_delete=CASCADE)
health_statuses.student_id     (FK, on_delete=CASCADE)
```

Serializers expose the field to clients under the name **`student_id`** — not Django's default
`student` — via `PrimaryKeyRelatedField(source='student')`. The wire format matches the column name.

---

## Rationale

**One identifier across every system.** The Registrar, Student Portal, Faculty System, and clinic
system all key on the same value. Option A would have required a cross-system mapping table and a
translation step in every integration, with a class of mismatch bugs where a local ID was used where
the shared one belonged. `student_id` is the join key across the entire architecture — see
[integration.md §3](../integration.md#3-shared-identifiers).

**No allocation responsibility.** The clinic system never issues identifiers, so it cannot issue a
duplicate or collide with a future Registrar change. It only validates that a supplied value is
available.

**Foreign keys propagate naturally.** Because the child's FK column is `student_id`, cascading deletes
and joins work on identically named columns across all four tables, and an ID read from any endpoint
is directly usable at any other.

**No duplicated identity data.** With `0003` removing the name columns, the clinic system stores no
student data it does not own. That eliminates a whole class of synchronisation drift with the
Registrar — there is nothing to fall out of date.

---

## Consequences

### Positive

- A single shared identifier across Registrar, Portal, Faculty, and clinic
- No ID allocation logic in this system, and no duplicate-ID risk
- FK columns consistently named `student_id` across all tables
- Clean cascades on student deletion, asserted by three model tests
- The `BigInteger` range comfortably covers realistic student numbers without collision risk

### Negative / accepted costs

- **The clinic system cannot create a student without knowing the Registrar's ID.** `POST
  /api/students/` fails without one, and returns `400` for a duplicate.
- **The ID format is owned by someone else.** If the Registrar ever switches to a non-integer or
  composite identifier, the column type and every integration must change. That constraint is
  imposed by this decision.
- **Sequential IDs leak enrolment volume.** If the Registrar assigns sequential numbers, the gap
  between two IDs reveals how many students enrolled between them. An opaque identifier would avoid
  this — a consideration worth raising with the Registrar.
- **Not portable.** Data cannot be meaningfully merged with another system that does not share the
  same student numbering.

### Open integration question

There is **no Registrar integration in the codebase** — no inbound endpoint, webhook, or import job.
Externally supplied IDs mean every student record was created by someone POSTing it or via Django
Admin. If the Registrar is expected to push students automatically, that importer does not exist and
the contract still needs to be specified. Tracked as **AG-12** in
[integration.md §7](../integration.md#7-agreements-log).

---

## Follow-on

- None. This decision is independent of
  [ADR-0001](0001-backend-framework-django-drf.md) and
  [ADR-0002](0002-split-consultations-from-health-records.md).