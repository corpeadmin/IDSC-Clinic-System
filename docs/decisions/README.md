# Architecture Decision Records

Records of significant decisions, with the context and consequences that motivated them.

## Format

Each ADR is a Markdown file named `NNNN-short-slug.md` and contains: Context, Decision, Rationale
(including why the alternatives were rejected), Consequences, and any open questions.

ADRs are **immutable once accepted**. A decision that turns out to be wrong is superseded by a new ADR
that links back to it; the original is edited only to mark it superseded.

## Index

| ADR | Title | Status | Date | Supersedes |
| :--- | :--- | :--- | :--- | :--- |
| [0001](0001-backend-framework-django-drf.md) | Backend framework — Django 6.1 with Django REST Framework | Accepted | 2026-08-18 | — |
| [0002](0002-split-consultations-from-health-records.md) | Split consultations into their own table | Accepted | 2026-09-22 | Original `HealthRecord` schema |
| [0003](0003-externally-supplied-student-id.md) | Externally supplied `student_id` as the primary key | Accepted | 2026-08-22 (completed 2026-09-06) | The `0002` auto-increment approach |

## Related

- [architecture.md](../architecture.md)
- [data-model.md](../data-model.md)
- [integration.md](../integration.md)
- [design-system.md](../design-system.md)