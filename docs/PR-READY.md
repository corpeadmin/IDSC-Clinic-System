# Add JWT recovery and deploy the Clinic school demo

Login issues revocable JWTs while preserving session compatibility. Recovery validates the registered email and sends an expiring, single-use link; successful reset revokes sessions and JWTs. Owner/Admin/Staff permissions and the verified business API contract are preserved.

The cloud profile serves the frontend on Vercel, the Docker API on Render Free and persistent Clinic data on Supabase PostgreSQL. Brevo HTTPS supports recovery without SMTP. Startup provisions the first Owner before public serving, certificate verification stays enabled, and a test-gated main release workflow is prepared.

Validation: all 12 quality jobs passed for deployed code commit `4645e34`, including both databases, container, browser, Postman and contract checks. Staged and public frontend/API checks passed; hosted Owner login and JWT dashboard passed. Brevo accepted a hosted reset email; inbox receipt/redemption await user confirmation. See [CURRENT-VALIDATION.md](CURRENT-VALIDATION.md).

Live demo: https://idsc-clinic-management.vercel.app. The initial release was manual after CI; main is unchanged. Production environment configuration and an actual main release remain pending, along with a real provider gateway call. Hosted Registrar/Inventory remain process-local mocks; free backend cold starts apply. No credentials or recovery links are included.

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
