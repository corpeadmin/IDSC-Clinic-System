# PR title

Complete clinic interface and secure account management

# Description

The clean repository had a verified backend but a starter frontend, while the strongest legacy interface simulated credentials and browser-only record changes. This branch reuses that layout and connects health records, consultations, statuses, dispensing and rollback, all four reports and staff management to the existing API. It adds a persistent light/dark theme preference and softens the light palette.

Settings now supports self-service password changes through `POST /api/auth/password/change/`. The endpoint checks the current password, matching confirmation, non-reuse and configured Django validators, then hashes the password. The current session is rotated and retained; other sessions expire. Authentication and CSRF remain enforced.

Settings also supports username changes after current-password verification. Administration can list and create additional Clinic administrators; creation requires the existing admin's password and a strong, confirmed password for the new account. Newly created administrators receive the Clinic role without Django superuser access.

All 45 original API definitions and the original 167 backend tests remain unchanged. The additive contract now contains 43 paths and 70 operations. There are 13 password-change tests, 18 account-management tests and 23 lifecycle tests. The original Postman collection is preserved, with separate password and account-management collections added.

Branch selection is documented in `docs/CONSOLIDATION-AUDIT.md`; password behavior is in `docs/PASSWORD-CHANGE.md`. Latest executed results are in `docs/INTEGRATION-VALIDATION.md`.

Validation: 257 Django tests; configuration/migration/schema checks; matching static/dynamic inventory; both Redocly lints; all five Newman collections (139 requests / 150 assertions); frontend lint/build; all six browser stories (clinical, staff, password, new-admin/username, account lifecycle and role hierarchy); theme persistence and desktop/mobile visual checks.

Clinic business data remains process memory with mock external services. Durable business storage, real external connectors, visual sign-off, branch protection and teammate approval remain release gates. Merge through a reviewed PR only. Synced school source documents and main are untouched.

Administrators and staff now have deactivate/reactivate and permanent-delete controls. New delete APIs require actor-password verification; all lifecycle APIs enforce active-admin, CSRF, self/last-admin, system-admin and role-boundary guards. Deactivation revokes database sessions and deletion preserves clinical records. Directory capability fields explain disabled controls. See `docs/ACCOUNT-LIFECYCLE.md`.


## Owner, Admin and Staff

Owner manages Admins and Staff; Admin manages Staff only; Staff uses clinic features without account management. Owner accounts are protected from deletion/deactivation. Existing Django superusers are Owners; clinic groups retain their current Admin/Staff roles. Session responses expose the role. Admin account detail now supports GET/PUT/PATCH as well as DELETE, and account edits support validated usernames. See [ROLE-HIERARCHY.md](ROLE-HIERARCHY.md) for the permission matrix and API details. This policy supersedes earlier descriptions allowing Admins to manage Admins.


## Staff pages and Admin capacity

Staff management now shows ten accounts per page with working Previous/Next controls and search-aware page counts. `GET /api/v1/users/` returns the Clinic pagination envelope, default/max `page_size=10`. Admin creation has a server-enforced five-account maximum, including inactive Admins and excluding Owners; capacity returns 409 until an Admin is deleted. See [ACCOUNT-LIMITS.md](ACCOUNT-LIMITS.md) for details and validation fixtures.


## Registrar and Inventory demo workflows

Consecutive visible record labels, Owner/Admin-only clinical/history deletion, Get student by Registrar ID, automatic profile/status updates, Owner-operated Mock Registrar/Inventory workspaces, medicine notifications and selected/all restock requests with Inventory fulfillment are now connected to backend APIs. Internal record IDs stay stable; deleting dispensing history never reverses stock. These mock data reset on backend restart. See [EXTERNAL-WORKFLOWS.md](EXTERNAL-WORKFLOWS.md) for roles, routes, examples and demonstration limits. Current inventory: 43 paths / 70 operations.


Latest validation: 257 backend tests; nine browser workflows across regression runs; original and External-workflows collections total 79 requests / 86 assertions; frontend lint/build, configuration/migration checks and both schema lints pass. See EXTERNAL-WORKFLOWS.md and INTEGRATION-VALIDATION.md for the intentional permission changes, demonstration steps and process-local mock data limitation.
