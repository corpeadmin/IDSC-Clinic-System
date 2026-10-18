# Administrator and staff account lifecycle

## API

| Method | Route | Result |
|---|---|---|
| DELETE | `/api/v1/admins/{user_id}/` | Permanently delete an administrator; 204 |
| POST | `/api/v1/admins/{user_id}/deactivate/` | Deactivate an administrator; 200 |
| POST | `/api/v1/admins/{user_id}/activate/` | Reactivate an administrator; 200 |
| DELETE | `/api/v1/users/{user_id}/` | Permanently delete a staff account; 204 |

Existing staff activation/deactivation routes remain and now revoke sessions on deactivation. All lifecycle writes require session authentication, CSRF and an active Clinic administrator. DELETE requests additionally require JSON `current_password` for the acting administrator. Invalid passwords return 400 with field errors; anonymous callers receive 401, unauthorized callers 403, unknown/wrong-role targets 404, and self-removal or conflicting states 409.

## Safety and scope

- You cannot deactivate or delete your own account. At least one active administrator must remain.
- Clinic administrators cannot change a system administrator's access. Another system administrator must perform that action.
- Staff routes reject administrator targets, including accounts belonging to both role groups.
- All administrator lifecycle mutations lock base User rows in a consistent order under a transaction, then recheck the actor and target. PostgreSQL avoids DISTINCT/join locking limitations by locking User rows through an ID subquery. SQLite retains the verified development runtime.
- Deactivation revokes matching unexpired sessions from Django's configured database session backend. Reactivation restores login access without reviving those sessions.
- Deletion removes the login account and its sessions; Clinic medical records remain. Usernames may be reused after permanent deletion.

The administrator directory adds read-only `is_system_admin`, `can_manage`, and `management_restriction` fields. These are UI hints and do not replace backend checks. Other existing account response shapes are unchanged.

## Interface

Administration offers Deactivate (or Activate for inactive accounts) and Delete in both administrator and staff tables. Protected controls are disabled with an explanation. Every action requires confirmation. Delete explicitly explains permanence and asks for the acting administrator's password. Failed validation leaves the dialog open for correction; successful operations refresh the directory. No passwords are saved in browser storage.

## Verification

Twenty-three backend tests cover state changes, fresh-login requirements, session revocation, deletion, active/inactive targets, CSRF, permission denial, actor reauthentication, self/last-active-admin safeguards, protected system users, mixed-role route bypass, directory capabilities, unrelated-session preservation and medical-record preservation. Existing tests remain.

`frontend/tests/account-lifecycle.spec.js` exercises cancel, deactivate/reactivate, blocked inactive login, wrong deletion password, successful administrator/staff deletion and absence after reload. The existing four browser stories cover clinical workflows, staff management, passwords and new admin/username changes.

`postman/Account-lifecycle.postman_collection.json` creates and deletes isolated accounts in a disposable database. It must not be run against real accounts. See latest results in `INTEGRATION-VALIDATION.md`.

Current inventory: 35 paths / 53 operations, including 3 public and 50 protected operations. No database migration or business-data repository change is needed.


## Updated role policy

The [Owner/Admin/Staff hierarchy](ROLE-HIERARCHY.md) supersedes the earlier two-role permission descriptions above. Only Owner manages Admins; Owner and Admin manage Staff. Owner accounts are excluded from directories and protected from deletion/deactivation. Owner can remove the last regular Admin because Owner remains available.
