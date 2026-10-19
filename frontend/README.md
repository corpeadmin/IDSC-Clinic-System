# IDSC Clinic frontend

React/Vite UI integrated with the verified Django API. Start Django on `127.0.0.1:8002`, then run `npm ci` and `npm run dev` here. Open `http://127.0.0.1:5173`. Use an actual Django account; there is no hard-coded demo login. Create an administrator with `python manage.py createsuperuser` from `backend/` after migrations.

Vite proxies `/api` to Django and keeps cookies/CSRF on the browser origin. Unsafe requests fetch a fresh CSRF token, including after login rotation. Production hosting must serve `/api` through a same-origin reverse proxy; `vite preview` alone does not provide the backend proxy.

Clinic business records use the verified in-memory service/repository and survive browser reloads but reset when Django restarts. Registrar and Inventory are deterministic mock integrations. Do not use this runtime for real patient data.

## Validation

- `npm run lint`
- `npm run build`
- `npx playwright install chromium`
- Start both servers, set `CLINIC_TEST_USERNAME`, `CLINIC_TEST_PASSWORD`, and `CLINIC_TEST_NEW_PASSWORD` to an isolated test administrator, then run `npm run test:e2e`.

The browser test mutates school demo data, creates/deletes a health record, dispenses and rolls back medicine, reads reports, and logs out. Run against a fresh mock backend; additional validation covers consultations, statuses and staff management. Do not use real accounts/data.

API behavior is centralized in `src/api.js`: session cookies, CSRF, error status/body preservation and pagination. UI layout provenance and branch comparison are documented in `../docs/CONSOLIDATION-AUDIT.md`.

Settings includes a self-service password dialog with field-specific validation errors. The password test requires an isolated administrator and two strong passwords; it restores the original password afterward.

Settings also supports username changes with current-password verification. Administration lists Clinic administrators and provides Add administrator; creation verifies the acting admin's password and the new account's password confirmation. New accounts have the Clinic administrator role. The account-management browser story creates an isolated new admin, checks its access, renames it and verifies the new login.

Administrator and staff tables now offer deactivate/reactivate and delete. Delete asks for the acting administrator's password; self/protected accounts are disabled, and all backend safeguards still apply. The lifecycle browser story creates and removes disposable accounts.


Owner sees Admin and Staff management; Admin sees Staff management only; Staff has no Administration access. The session `role` drives role labels and Owner controls, while the API enforces permissions. Owners use Settings to change their own username/password. See `docs/ROLE-HIERARCHY.md`. Six browser stories cover clinic and account flows.

Staff management has ten-row pages, Previous/Next controls, a filtered range/count and search page reset. Owner sees a five-Admin capacity indicator and disabled creation at capacity; the API enforces the limit. See docs/ACCOUNT-LIMITS.md for the isolated boundary test fixtures.


Owner navigation now includes Mock Registrar and Mock Inventory. Students has Get student by ID; profiles/status refresh every five seconds and on focus. Medicine stock has unread Inventory notifications and ALL/SELECTED restock requests; Owner fulfills in Mock Inventory. Record display numbers are consecutive per student, with stable API IDs. Staff cannot delete clinical records/history; Owner and Admin can. Sidebar scrolls on short screens. Mock business data resets on backend restart. See docs/EXTERNAL-WORKFLOWS.md.

The local API proxy defaults to `http://127.0.0.1:8002`. Set `CLINIC_API_TARGET` before starting Vite to use a different backend address.
