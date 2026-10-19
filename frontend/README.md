# Clinic website

React/Vite UI connected to Django sessions and CSRF. Follow [SETUP.md](../SETUP.md) for both servers. Inside frontend run `npm ci` then `npm run dev`. Normal address: http://localhost:5173. Default API target: http://127.0.0.1:8002; set CLINIC_API_TARGET before starting Vite to change it.

Fresh databases show first-Owner registration with automatic Dashboard login. Later visits show shared login. Settings changes own credentials; Owner manages Admin/Staff, Admin manages Staff, Staff has no Administration. Owner alone operates Mock Registrar/Inventory. Clinic features include records/statuses, dispensing/rollback, reports, restocks, notifications and light/dark theme. See [README.md](../README.md).

src/api.js handles cookies, fresh CSRF tokens, errors and pagination. Vite proxies /api. Production needs a same-origin API reverse proxy; vite preview alone does not provide it. Mock business state resets on backend restart; accounts persist separately.

## Validation

```powershell
npm run lint
npm run build
npx playwright install chromium
```

Browser tests mutate accounts/data and credentials. Use a disposable database/backend, an isolated Owner, strong passwords and seeded mock data (CLINIC_EMPTY_START=0). The password story restores the original password.

```powershell
$env:CLINIC_TEST_BASE_URL="http://localhost:5173"
$env:CLINIC_TEST_USERNAME="your_disposable_owner"
$env:CLINIC_TEST_PASSWORD="your_disposable_owner_password"
$env:CLINIC_TEST_NEW_PASSWORD="a_different_strong_test_password"
npx playwright test clinic.spec.js password-change.spec.js account-management.spec.js account-lifecycle.spec.js role-hierarchy.spec.js external-workflows.spec.js mock-catalog.spec.js
```

Replace example values with actual disposable credentials. For account-limits.spec.js, additionally provision eleven Staff named seedstaff_00 through seedstaff_10 in CLINIC_STAFF and start with an empty Admin directory. Run that boundary story separately against its fixtures; see [ACCOUNT-LIMITS.md](../docs/ACCOUNT-LIMITS.md). modal-focus.spec.js intercepts API responses and needs a running frontend but no live credentials.

Run the registration story separately against a freshly migrated database with no Owner or completed registration latch. It creates its own Owner:

```powershell
$env:CLINIC_TEST_FIRST_RUN="1"
npx playwright test owner-registration.spec.js
Remove-Item Env:CLINIC_TEST_FIRST_RUN
```

Point CLINIC_TEST_BASE_URL at the matching isolated frontend. Additional origins/ports need corresponding Django CORS/CSRF settings; default approved origins use port 5173. npm run test:e2e runs discovered tests; it does not provision accounts or special fixtures. Registration is skipped unless explicitly enabled.

[CURRENT-VALIDATION.md](../docs/CURRENT-VALIDATION.md) separates latest checks from historical evidence. Details: [roles](../docs/ROLE-HIERARCHY.md), [external workflows](../docs/EXTERNAL-WORKFLOWS.md), [Owner setup](../docs/OWNER-REGISTRATION.md).
