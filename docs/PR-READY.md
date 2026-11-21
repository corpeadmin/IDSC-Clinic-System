# Record the verified automated Clinic release

The Clinic is deployed at https://idsc-clinic-management.vercel.app. Main commit `f43769b` passed all 13 jobs in [run 44891807127](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/44891807127), including the protected production release. Render publishes the tested SHA; Vercel stages, checks and promotes the exact frontend deployment through the project-scoped API.

Independent checks passed for Owner login, JWT dashboard access, Swagger, public health and static assets. The live API matches all 50 paths and 77 operations in the committed contract. Documentation reconciles earlier pending setup language with the successful release and preserves dated failure diagnostics. This documentation follow-up changes no application code or API contract.

Real Registrar/Inventory gateway integration remains pending because the partner systems are unfinished. Hosted mocks demonstrate workflows but do not satisfy the real integration requirement. The user confirmed recovery email receipt and the hosted reset form; completed hosted password reset remains unverified. See [RELEASE-EVIDENCE.md](RELEASE-EVIDENCE.md) for evidence and operational limits.

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
