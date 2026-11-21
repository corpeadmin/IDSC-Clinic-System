# Production release evidence

Verified 21 November 2026. This records the observed release; it does not certify every school submission requirement as complete.

## Published system

- Website: https://idsc-clinic-management.vercel.app
- Swagger UI: https://idsc-clinic-management.vercel.app/docs
- Health: https://idsc-clinic-management.vercel.app/health
- Repository: https://github.com/microwaveTuesday/IDSC-Clinic-System
- Deployed main commit: `f43769bf88c94289f03f05fcee17c808180f670c`
- [Successful Actions run 44891807127](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/44891807127)
- [Production release job](https://github.com/microwaveTuesday/IDSC-Clinic-System/actions/runs/44891807127/job/136809498082)
- [Merged promotion fix PR #7](https://github.com/microwaveTuesday/IDSC-Clinic-System/pull/7)

## Observed validation

All 13 jobs succeeded: SQLite and PostgreSQL backend jobs, OpenAPI contracts/Redocly, frontend lint/build, dependency checks, private HTTPS container smoke, Postman regression, five browser suites, and the actual production release.

The owner approved this exact commit in the protected production environment. The release verified Render's intended repository, main branch and disabled independent auto-deploy, deployed the tested SHA and waited until live. It staged the frontend without assigning production domains, passed staged checks, promoted through Vercel's project-scoped API, confirmed the stable domain belongs to that exact deployment, and passed final public checks.

Independent checks after release passed:

| Check | Result |
| --- | --- |
| Public frontend and health | PASS |
| Database-backed setup; Owner registration closed | PASS |
| API no-store response | PASS |
| Swagger UI and OpenAPI | PASS |
| Anonymous protected dashboard rejected | PASS |
| Existing Owner login issues JWT | PASS |
| JWT-authenticated dashboard | PASS |
| Live operation contracts equal committed OpenAPI | PASS: 50 paths, 77 operations |
| Django admin CSS | PASS |

These read-only checks and login did not create or delete clinical records or change the Owner password. The recipient separately confirmed that the cloud Brevo recovery email arrived and opened the deployed reset form. Completed hosted reset redemption has not been confirmed.

## Configuration and limits

Production is restricted to main with owner review and administrator bypass disabled. Render independent auto-deploy is off; Vercel has no independent Git deployment. The configured GitHub deployment secret values are not included in evidence. Initial Owner bootstrap variables were removed from Render; an earlier configuration restart and subsequent login verified that the existing Owner persisted. Do not re-import stale bootstrap settings.

Clinic data and accounts use Supabase PostgreSQL with certificate and hostname verification. Hosted Registrar/Inventory remain process-local mocks and can reset on backend restart or free-service spin-down. Free backend cold starts remain possible. Recovery uses Brevo HTTPS. Rotate the project-scoped Vercel deployment token before its configured 19 February 2027 expiration. GitHub reports action-runtime deprecation warnings; the run succeeded, but pinned action upgrades remain maintenance work.

The earlier dbdfbb4 and 55ef629 runs failed during CLI profile lookup; they are not successful full releases. Their diagnostics remain in [CURRENT-VALIDATION.md](CURRENT-VALIDATION.md). The successful project-specific API fix retains token scope and deployment protections.

## Remaining school-project work

A real working call through the agreed partner API gateway is still required. Mocks do not establish that connectivity. Obtain and record the actual Registrar or Inventory contract, gateway origin, server authentication method, synthetic test input, status mappings and timeout/offline behavior. Inventory also requires idempotency, reconciliation and reversal semantics. See [REAL-SYSTEM-INTEGRATION.md](REAL-SYSTEM-INTEGRATION.md).

Complete the group-authored technical paper, diagrams, contribution table and showcase evidence against the instructor's requirements. This release record is operational evidence, not a completed technical paper. Keep the repository, hosted site and database available until grades are released.
