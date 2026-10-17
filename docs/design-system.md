# Clinic frontend design baseline

The integration branch reuses the clinic interface from `corpeadmin/IDSC-Clinic-System` at `de0246d`, selectively importing its layout, CSS and IDSC logo. The former starter UI and browser seed data are replaced. This is repository implementation evidence; final Figma/instructor approval has not been independently verified.

## Implemented interface

- Responsive sidebar and mobile menu, dashboard cards, student search/course filter and detail tabs.
- Clinic-owned health record, consultation and health-status forms; Registrar students remain read-only.
- Inventory medicine catalog projection, stock filtering, dispensing history and confirmed rollback.
- Authenticated account information and backend-authorized staff management.
- Accessible field labels, visible focus outlines, dialog focus trap/Escape dismissal and restored focus.
- Loading state, API errors, disabled mutation submit buttons and delete/rollback confirmation.

## Styling

`frontend/src/index.css` contains the recovered component styles and responsive rules. Core colors include clinic green `#168153`, text `#263b32`, page background `#f7f9f8`, and white panels. Typography uses DM Sans and Manrope with local sans-serif fallback. The logo is `frontend/src/assets/idsc-logo.png`.

The UI loads data from the server, never from demo seeds. The mock backend limitation is disclosed in the dashboard and setup documentation. The authentication contract does not expose roles; admin navigation is enabled only after `/api/v1/users/` succeeds, while every privileged request is still enforced by the backend.

## Verification

See `INTEGRATION-VALIDATION.md` and the Playwright flow in `frontend/tests/clinic.spec.js`. Changes to visual design should update this document and obtain the team’s approval against the authoritative Figma prototype.
