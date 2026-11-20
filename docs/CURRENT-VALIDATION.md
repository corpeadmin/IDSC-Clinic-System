# Current validation record

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
