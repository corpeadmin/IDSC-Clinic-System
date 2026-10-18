# Username and administrator management

## Username changes

POST `/api/auth/username/change/` accepts `new_username` and `current_password`. It always updates the authenticated account, never an account chosen by a supplied ID. The current password is verified against a freshly read, locked account. Django username validation, a 150-character limit, trimming, Unicode normalization and case-insensitive duplicate checks apply. Unchanged names are rejected. Database uniqueness conflicts are translated into a field error.

Success is HTTP 200 with the same account shape as `/api/auth/me/`. The existing session stays authenticated and future sign-ins use the new username. Validation errors are HTTP 400 Problem Details; authentication and CSRF are mandatory.

Settings > Change username provides the form, field errors, pending state, immediate profile update and confirmation. Passwords are not written to browser storage.

## Additional administrators

GET `/api/v1/admins/` lists users in `CLINIC_ADMIN` plus existing Django superusers, without duplicates. POST at the same path creates an active Clinic administrator. Both require `IsClinicAdmin`; staff are denied HTTP 403 and anonymous callers HTTP 401.

Creation requires `username`, `password`, `confirm_password`, and the acting administrator's `current_password`. Optional profile fields are `first_name`, `last_name`, and `email`. Django password validators apply to the new account, confirmation must match, and the actor must supply their own correct password. User creation and group assignment are atomic.

The created account gets only the Clinic `CLINIC_ADMIN` role; `is_superuser` and Django's `is_staff` remain false. This still permits Clinic dashboard, staff management and creating other Clinic administrators. Supplied role/superuser flags cannot grant broader access. The existing staff-creation endpoint still creates staff only. Secrets are write-only and excluded from responses.

Administration > Add administrator opens the form. Administrators are listed separately from staff. Settings displays Clinic access instead of the unrelated Django staff flag. The later lifecycle extension adds administrator deletion, deactivation and reactivation with self/last-admin protections; it still does not allow changing someone else's username. See `ACCOUNT-LIFECYCLE.md`.

## Contract and validation

These features add two paths and three operations to the password-change baseline: current totals are 32 paths / 49 operations (3 public, 46 protected). Every original operation remains unchanged; no database migration is needed.

Eighteen backend tests cover self-only updates, current-password checks, valid/invalid/duplicate/normalized names, session retention and old/new login; admin-role creation, no superuser escalation, actor authorization, CSRF, password confirmation/strength, duplicate names, directory contents, and new-admin access/creation capability. The original staff endpoint cannot promote a new account.

`frontend/tests/account-management.spec.js` creates an isolated Clinic administrator, verifies access, checks duplicate/wrong-password errors, renames it and validates session retention and old/new login. The account and password browser stories use `CLINIC_TEST_USERNAME`, `CLINIC_TEST_PASSWORD` and `CLINIC_TEST_NEW_PASSWORD` with an isolated test administrator.

`postman/Account-management.postman_collection.json` adds a 19-request test flow. It creates an administrator and renames/restores that isolated account; run only against a disposable framework database. Existing Postman collections are unchanged. See `INTEGRATION-VALIDATION.md` for execution evidence.

Executed results: 198 Django tests, all four browser stories, and all three API collections (75 requests / 80 assertions) passed. Both schema lints, configuration/migration checks and frontend lint/build passed.


## Updated role policy

The [Owner/Admin/Staff hierarchy](ROLE-HIERARCHY.md) supersedes the earlier two-role permission descriptions above. Only Owner manages Admins; Owner and Admin manage Staff. Owner accounts are excluded from directories and protected from deletion/deactivation. Owner can remove the last regular Admin because Owner remains available.
