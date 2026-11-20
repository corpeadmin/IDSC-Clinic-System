# Add JWT login and Gmail password recovery

Current local head: `integration/final-jwt`; base: `submission/clinic-final-v2` at `ad361f1`. Implementation commit `2267508` has been pushed to `corpeadmin/IDSC-Clinic-System`; All 12 jobs passed for code commit `c6a3302`: [successful run](https://github.com/corpeadmin/IDSC-Clinic-System/actions/runs/44762774676).

Login now issues revocable JWT access tokens while preserving session compatibility. The browser holds tokens in memory and renews through its CSRF-protected session. Forgot password opens an email form and sends a 30-minute, single-use reset link to the saved recovery address. Unknown emails show a 404 error; mail failures show 503. Resetting the password revokes existing sessions and JWTs. The OpenAPI contract, SMTP example configuration, deployment environment wiring and browser/backend regressions are updated.

Validation: 340 of 342 backend tests passed with a test-only fast hasher; two PostgreSQL-only tests skipped. All 18 recovery tests passed with configured hashing. Browser recovery, frontend lint/build, static/runtime contract equality and Redocly lint passed. Real Gmail authentication/submission succeeded and the user confirmed receipt and reset. No credentials, recipient addresses or reset tokens are included in this description. See [CURRENT-VALIDATION.md](CURRENT-VALIDATION.md).

Public hosting and a real institutional API gateway call remain unverified. All 12 GitHub Actions jobs passed, including SQLite/PostgreSQL tests, backup/restore, browser workflows, dependency audits, Postman, contract checks and private HTTPS container smoke. Compatible development dependency updates and containerized PostgreSQL 16 backup clients resolved the initial CI failures. Deployment after tests on main remains outstanding.

## Historical verification PR description

# Verify final-project reliability, restoration and CI

Base: improvement/clinic-final-10of10. Head: improvement/clinic-final-verification.
Clean repository only; this draft does not merge or alter PR #2.

The previous branch lacked automated CI and a verified restore procedure, and
mock stock reset while clinical rows persisted. This pass adds fixture-isolated
Actions jobs, physical SQLite/PostgreSQL restore exercises, a separately owned
optional durable simulated Inventory ledger, and an ambiguity fence that refuses
unsafe retries after an interrupted external operation.

It preserves default mocks and all 294 inherited tests, adds 14 backend
regressions and an expired-session browser story, tightens login validation,
expires/purges replay bodies while retaining duplicate-operation tombstones,
minimizes error logs, and supplies a private HTTPS/Gunicorn/PostgreSQL deployment
profile with an executed restart smoke test. API routes remain 45 paths and 72
operations, with static/runtime schema equality checked in CI.

Validation and remaining limits: docs/VERIFICATION-RESULTS.md,
docs/VERIFICATION-SECURITY.md, docs/INVENTORY-RECOVERY.md,
docs/BACKUP-RESTORE.md and docs/KNOWN-LIMITATIONS.md. Real provider contracts,
public institutional hosting and compliance certification remain unavailable.
No real medical information or production credentials were used.
