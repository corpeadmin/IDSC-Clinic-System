# Current validation record

## Successful automated production release - 21 November 2026

Commit `f43769bf88c94289f03f05fcee17c808180f670c` completed [main run 44891807127](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/44891807127) with **all 13 jobs successful**. The operator approved this exact commit through the protected production environment. Render deployed the tested backend SHA; the staged frontend passed checks, project-scoped REST promotion assigned its stable domain, and final public checks passed.

Independent post-release checks passed: public frontend, health, database-backed setup, closed Owner registration, no-store API, Swagger, anonymous dashboard rejection, Owner login, JWT-protected dashboard and admin CSS. The live API contract equals the committed contract: 50 paths and 77 operations. See [RELEASE-EVIDENCE.md](RELEASE-EVIDENCE.md).

The dated sections below are historical snapshots; their pending statements describe the state at that time. The two failed release attempts were superseded by this successful run. Real partner integration and completed hosted reset redemption remain unverified.

## Project-token promotion follow-up - 21 November 2026

The second gated run for 55ef629 (44890616421) passed all 12 quality jobs and deployed the exact backend revision, but explicit CLI scope caused staging to fail during user-profile lookup. No production frontend promotion occurred. The previous scope-only diagnosis was insufficient.

The follow-up restores the staging invocation that already succeeded with the project-scoped token and uses Vercel's documented project-specific promotion API. It verifies the configured team owns the project, the staged deployment ID/project/URL match, and the deployment is READY for production before one promotion request. It then waits for the stable public domain to appear as a direct alias of that exact deployment. No user-profile lookup, wider token, protection disablement or manual promotion is substituted for a successful workflow. Synthetic tests cover wrong targets, preview/unready deployments, unsafe URLs and uncertain outcomes. A fresh gated release must prove the fix.

Provider documentation: https://vercel.com/docs/rest-api/projects/point-production-traffic-to-a-given-deployment and https://vercel.com/docs/rest-api/projects/find-a-project-by-id-or-name.

## First gated main release diagnostic - 21 November 2026

All three production secret names were verified without reading their values, and CLINIC_DEPLOY_ENABLED was enabled. PR #5 merged as dbdfbb4. All 12 quality jobs passed in [main run 44875708009](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/44875708009), then the operator approved the production environment.

The release authenticated to Render and deployed exact commit dbdfbb4 (deployment dep-dc0m6rrm8hqs73ev7ll0). Frontend staging and same-origin checks passed. Promotion failed with Vercel CLI User not found (404), and the final public check was skipped. This run is not a successful full release. The workflow follow-up explicitly supplies the verified Vercel team ID for both staging and promotion, and the project ID for staging. A fresh gated main run must prove the fix; no manual promotion is substituted for that evidence.

## Ownership and release configuration - 21 November 2026

GitHub verified the transfer to microwaveTuesday/IDSC-Clinic-System with administrator permissions. PR #4 was merged by the repository operator into main at 23cf46c; [main quality CI passed](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/44869516541), with the release job skipped. The local legacy remote now uses the new URL; origin remains the separate Clean repository. Historical evidence below preserves the original repository names and commit references.

Render's existing service now targets the transferred repository and main branch. Docker and deploy/Dockerfile.backend are preserved; Auto-Deploy is Off. GitHub production is created with main-only branch policy, microwaveTuesday as required reviewer and administrator bypass disabled. All five non-secret hosting variables are saved. Production deployment secrets and the enable flag remain pending; no successful main release is claimed.

The other groups' Registrar and Inventory systems are reported unfinished. Integration inputs remain documented; mocks are not evidence of a real gateway call.

## Public cloud deployment - 21 November 2026

Deployed tested commit `4645e34` from `integration/final-jwt` after [all 12 quality jobs passed](https://github.com/corpeadmin/IDSC-Clinic-System/actions/runs/44865005481). Render service `srv-dc0hvj3m8hqs73ej4cd0` reports Live; Vercel deployment `dpl_HFU5vLRHPy1tvWnHgaSuRyoARcTS` was staged, checked, then promoted. This was a manual initial release; main is unchanged and the production Actions job has not run.

- Public website: https://idsc-clinic-management.vercel.app
- Swagger: https://idsc-clinic-management.vercel.app/docs
- Backend health: https://idsc-clinic-api.onrender.com/health
- Supabase password authentication and certificate/hostname verification passed. Render completed Django migrations and provisioned the first Owner before listening.
- Public frontend, same-origin health, database-backed setup, no-store API, schema and Swagger passed. Anonymous dashboard returns 401; Owner login and JWT dashboard return 200. Public registration is closed.
- Collected Django admin CSS returns 200 directly from Render. Browser visibly shows the public Clinic login page.
- Hosted password-reset request returned 200 through Brevo. The user confirmed inbox receipt and that the link opens the hosted reset form. Completed password reset remains unverified; the test request did not change the password.
- The smoke checker now accepts both HTML and API response types, avoiding a false 406 on Swagger. No backend contract change.

Bootstrap cleanup: INITIAL_OWNER_USERNAME, INITIAL_OWNER_PASSWORD and INITIAL_OWNER_EMAIL were removed from Render. Configuration restart `dep-dc0i5rs0916s73bqlte0` reached Live on the same code commit. Startup reported the existing Owner unchanged, and public smoke plus Owner login passed after restart. This verifies account persistence; no new clinic-record persistence claim is made. Both follow-up commits `72e24b0` and `5d98ff0` also passed CI.

Remaining: configure protected production CI variables/secrets with the repository administrator and validate a real push-to-main release; verify completed hosted reset redemption and database restart persistence; implement one agreed real provider gateway call. Registrar/Inventory are still process-local mocks on this free profile. Free backend cold starts remain possible.

## Cloud preparation - 21 November 2026

The free-hosting profile, Brevo HTTPS mail transport, hosted Owner provisioning, PostgreSQL TLS settings, optional static middleware, frontend routing package and test-gated release job are prepared. See [CLOUD-RELEASE.md](CLOUD-RELEASE.md). The public website and real Brevo inbox delivery are not yet verified.

Local validation: 356 backend tests discovered with the test-only fast hasher; 354 passed and two PostgreSQL-only tests skipped. Sixteen focused configuration/Owner/email-backend tests passed with configured hashing. Eight deployment guard/packaging tests passed. Frontend lint/build, migration drift and static/runtime contract equality passed; 50 paths/77 operations unchanged. Collected admin CSS was served successfully by the hosted static middleware.

All 12 quality jobs subsequently passed for `7d13037`, including PostgreSQL and the actual container smoke: [CI run](https://github.com/corpeadmin/IDSC-Clinic-System/actions/runs/44862660702). The production-release job was correctly skipped on the integration branch. The restricted-key diagnostic follow-up has a separate CI run.

A dedicated Free Supabase project in Singapore and the Vercel Hobby project `idsc-clinic-management` were provisioned. Its readable domain is reserved but has no deployment yet. Database TLS certificate/hostname verification passed using the official Supabase CA; database password authentication and migrations remain pending. Render remains a Free-plan draft. The Brevo sender was visibly Verified; the private API key and actual delivery still require configuration/testing. No credentials are recorded here. Main is unchanged.

## Current local validation — 20 November 2026

Work branch: `integration/final-jwt`, based on `submission/clinic-final-v2` at `ad361f1`. Implementation commit `2267508` is published to `corpeadmin/IDSC-Clinic-System` on this branch. All 12 GitHub Actions jobs passed for code commit `c6a3302`: [successful run](https://github.com/corpeadmin/IDSC-Clinic-System/actions/runs/44762774676). JWT login, memory-held browser tokens, revocable access grants and email-based password recovery are implemented. Existing Owner/Admin/Staff permissions remain in force.

| Check | Result and scope |
| --- | --- |
| Full SQLite backend suite | 342 discovered: 340 passed, two PostgreSQL-only skips; test-only fast hasher, production hashing unchanged |
| Recovery tests with configured hashing | All 18 passed |
| Browser recovery | Passed with an isolated file outbox: unknown email error, link redemption, password validation, old-password/JWT rejection, new login and single-use link |
| Gmail delivery | SMTP authentication and real reset submission succeeded; user confirmed email receipt and a working reset |
| Frontend | ESLint and production build passed |
| API contract | Runtime/static equality and Redocly lint passed; 50 paths, 77 operations, nine public and 68 protected |

Recovery sends only to the saved email of an active account with a usable password. Unknown/ineligible addresses return 404; mail failures return 503. Reset links expire after 30 minutes. Successful reset revokes existing sessions and JWTs. Sender credentials are private environment configuration and are excluded from Git.

The user-requested local account reset was backed up; all prior accounts and sessions were removed while clinic table counts remained unchanged. First-run registration was verified open. The user then registered a fresh Owner and confirmed recovery worked. This was local maintenance, not a new account-deletion API or a change to the rule preventing Owner self-deletion.

Public deployment and real Registrar/Inventory gateway integration remain unverified. GitHub Actions passed all 12 jobs for `c6a3302`, including both database backends, physical restore, browser workflows, Postman, dependencies, contracts and private HTTPS container smoke. Automated tests use isolated fixtures; manual Gmail delivery is separately user-confirmed. See [JWT-AUTHENTICATION.md](JWT-AUTHENTICATION.md) and [PASSWORD-RECOVERY.md](PASSWORD-RECOVERY.md).

## CI follow-up

The first CI runs exposed outdated development dependencies and a PostgreSQL backup-client/server version mismatch. The lockfile now resolves Vite 8.3.8, ESLint 10.15.0, minimatch 11.0.9 and Zod 4.6.7; npm audit reports zero known vulnerabilities. Frontend lint/build and all browser jobs passed with these resolutions. The PostgreSQL job now uses backup clients from the same official PostgreSQL 16 image as its test service; physical backup/restore passed. Audit thresholds and test assertions were retained. These are checkout/CI fixes; no public deployment is claimed.

## Historical submission records

> Latest verification results: [VERIFICATION-RESULTS.md](VERIFICATION-RESULTS.md). The following submission-stage figures are historical.

# Current validation record

> Earlier submission background. Current improvement architecture/storage and evidence: [DATABASE.md](DATABASE.md), [IMPROVEMENT-VALIDATION.md](IMPROVEMENT-VALIDATION.md), [KNOWN-LIMITATIONS.md](KNOWN-LIMITATIONS.md).

As of 19 October 2026, submission/clinic-final-project implements the features in [README.md](../README.md). Historical reports retain their stage-specific counts; use this page for latest implementation evidence.

| Check | Recorded result and scope |
| --- | --- |
| Full backend suite | 273 passed with test-only MD5PasswordHasher override for execution speed; production settings unchanged |
| Owner-registration tests | All 16 passed with configured hashing |
| Simultaneous setup | Two requests against isolated SQLite returned 201/409; exactly one Owner |
| Fresh-install browser | Registration validation, automatic Dashboard, logout/reload/login and second-browser login-only passed |
| Modal-focus browser | Password focus across refresh and keyboard close/pending-state regression passed |
| Frontend | ESLint and production build passed |
| Django | System check and migration drift check passed |
| API | Static schema lint and runtime schema generation/validation passed; 45 paths/72 operations, 5 public/67 protected |
| Manual local reset | Empty accounts/sessions/Clinic/Registrar/Inventory and visible registration verified; this check did not create a new Owner |

Earlier clinical/account/external browser and Postman runs are recorded in [INTEGRATION-VALIDATION.md](INTEGRATION-VALIDATION.md), [TEST-EVIDENCE.md](TEST-EVIDENCE.md) and feature documents. They were not all rerun for Owner registration or this documentation update. The original collection's recorded baseline is 45 requests/46 assertions.

Backend tests use CLINIC_EMPTY_START=0 for standard seed fixtures. The faster-hasher suite checks behavior, not production hashing performance; the separate normal-hasher registration run covers configured hashing. Browser fixtures and disposable accounts are described in [frontend/README.md](../frontend/README.md).

Documentation review checks local Markdown links, complete endpoint-table coverage, runtime/static operation equality, stale current counts/branch names and Git whitespace. This does not imply another full browser or Postman run.
