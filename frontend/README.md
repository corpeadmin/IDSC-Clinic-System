# IDSC Clinic frontend

React/Vite UI integrated with the verified Django API. Start Django on `127.0.0.1:8000`, then run `npm ci` and `npm run dev` here. Open `http://127.0.0.1:5173`. Use an actual Django account; there is no hard-coded demo login. Create an administrator with `python manage.py createsuperuser` from `backend/` after migrations.

Vite proxies `/api` to Django and keeps cookies/CSRF on the browser origin. Unsafe requests fetch a fresh CSRF token, including after login rotation. Production hosting must serve `/api` through a same-origin reverse proxy; `vite preview` alone does not provide the backend proxy.

Clinic business records use the verified in-memory service/repository and survive browser reloads but reset when Django restarts. Registrar and Inventory are deterministic mock integrations. Do not use this runtime for real patient data.

## Validation

- `npm run lint`
- `npm run build`
- `npx playwright install chromium`
- Start both servers, set `CLINIC_TEST_USERNAME` and `CLINIC_TEST_PASSWORD` to an isolated test administrator, then run `npm run test:e2e`.

The browser test mutates school demo data, creates/deletes a health record, dispenses and rolls back medicine, reads reports, and logs out. Run against a fresh mock backend; additional validation covers consultations, statuses and staff management. Do not use real accounts/data.

API behavior is centralized in `src/api.js`: session cookies, CSRF, error status/body preservation and pagination. UI layout provenance and branch comparison are documented in `../docs/CONSOLIDATION-AUDIT.md`.
