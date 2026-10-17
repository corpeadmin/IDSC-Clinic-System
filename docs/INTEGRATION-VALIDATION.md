# Integration validation — 17 October 2026

## Preserved baseline

Integration base: `195580e` (`origin/fix/pre-main-integration`), tree-equivalent to clean `main` at `f37fd5c`. Backend implementation, all existing backend tests, `openapi.yaml` and the Postman collection are unchanged by this branch.

## Executed checks

| Check | Result |
|---|---|
| Django test suite | 167 discovered, 167 passed, zero failures |
| Django configuration check | No issues |
| Migration drift | No changes detected |
| Dynamic schema generation and validation | Passed |
| Static/dynamic inventory | Identical: 29 paths, 45 operations |
| Redocly static and dynamic lint | Both passed |
| Newman collection | 45 requests, 46 assertions, zero failures |
| Canonical `/api/v1/health` | Exact JSON `{"status":"ok"}` |
| `/docs` | HTTP 200 and Swagger markup |
| Unauthenticated protected resource | HTTP 401 and all canonical Problem Details fields |
| Frontend production build | Passed |
| Frontend ESLint | Passed |
| npm dependency audit | Zero vulnerabilities after compatible transitive dependency updates |
| Browser account/mobile flow | Passed: administrator staff creation/editing/deactivation/activation, staff login, hidden admin navigation, backend HTTP 403, desktop rendering and mobile navigation |
| Browser clinical flow | Passed: real session login, health-record create/edit/delete and reload persistence, consultation/status CRUD, dispensing/rollback, report rendering, logout and authenticated endpoint returning 401 afterward |

Both browser stories passed (clinical flow and administrator/staff flow; executed separately after fixes). Desktop (1440×1000) and mobile (390×844) screenshots were inspected.

Backend validation ran on Python 3.13.15; frontend validation used Node 24.21.0 and Chromium through Playwright. Tests used a locally created administrator with a random password, never committed. Newman ran before the fresh browser mock runtime. Test data, sessions, logs and credentials are excluded from Git.

## Browser verification details

The client sends credentialed requests through Vite's `/api` proxy. Every unsafe request first obtains a current CSRF token, so login rotation is respected. Mutation responses are followed by an API refresh, and reload persistence was checked against the same backend process. Backend errors remain visible in the page and editor. A successful write followed by a failed refresh is identified as saved, preventing an accidental duplicate submission.

During implementation, browser testing found and fixed an initial dashboard render before summary data arrived. Frontend checks also identified the legacy Tailwind import without a matching dependency, and rollback's status was corrected to canonical `COMPLETED`. Browser selectors were corrected to follow labeled required inputs and tab roles. These are recorded as fixes, not unresolved validation failures.

## Reproduction

Follow `frontend/README.md` for the two local servers and environment-based browser-test credentials. Run the existing Django suite from `backend`, then generate the dynamic schema with `python manage.py spectacular --file ../schema.generated.yaml --validate`. Lint the static and generated files using the existing `redocly.yaml`. Run the supplied Postman collection with Newman using an isolated administrator and override its username/password variables.

## Release boundaries

This validates integration against the supplied mock backend contract. It does not certify production clinical use, persistent business storage, real Registrar/Inventory connectors, an instructor-approved Figma match, GitHub branch protection or teammate approval. Those remain explicit release decisions. Main was not edited or pushed; consolidation is isolated on `integration/clinic-final`.
