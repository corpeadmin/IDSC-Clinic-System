# JWT authentication for the final project

Work branch: integration/final-jwt, based on submission/clinic-final-v2 at ad361f1. This change adds JWT authentication while preserving session compatibility and current Owner/Admin/Staff permissions. It does not implement public hosting or a genuine gateway integration.

## Login and protected requests

POST `/api/v1/auth/login/` accepts username/password and requires CSRF, as does the retained `/api/auth/login/` endpoint. Login returns the existing message/user plus access_token, token_type (Bearer) and expires_in. First-Owner registration returns the same token fields with its existing 201 response.

Send `Authorization: Bearer <access_token>` for protected API calls. A separate client with no browser cookies can use the JWT. Signature, algorithm, issuer, audience, required claims, expiry, token type and server receipt are verified. Invalid bearer credentials are rejected rather than falling back to an otherwise valid session cookie. Requests without a bearer header retain legacy session authentication and its CSRF requirements.

Tokens use HS256 with a purpose-separated key derived from the private Django SECRET_KEY. Claims are sub (user ID), jti (random grant ID), role, iss, aud, iat, nbf, exp and token_type. No password, medical data or raw session key is placed in the token. The role claim is descriptive: every request reloads the user and enforces current database roles and active state.

Default access lifetime is 900 seconds. JWT_ACCESS_SECONDS accepts 60 through 3600. Tokens are signed, not encrypted; clients must not treat their readable payload as secret storage. HTTPS remains required in deployment. The implementation follows [PyJWT's verification API](https://pyjwt.readthedocs.io/en/stable/api.html), with a fixed algorithm and explicit issuer/audience/required claims.

## Revocation and browser renewal

An AccessGrant stores the token's random identifier, user, expiry and server-side session reference. Authentication verifies the backing login session, current account status and current password authentication hash. This is intentionally stateful JWT authentication, allowing logout, revoked sessions, password changes and account deactivation/deletion to invalidate access before normal expiry.

The React client holds JWTs only in module memory, never localStorage or sessionStorage. On reload or shortly before token expiry, it obtains a new access JWT from POST `/api/auth/token/` using the HttpOnly session cookie and fresh CSRF header. Concurrent renewals share one request. This endpoint is session-only and does not accept an access token as a refresh credential. No standalone refresh JWT is issued.

Logout revokes the backing session even when called using only a bearer token. A browser password change rotates the retained session, invalidates old JWTs and obtains a new one. Other sessions/tokens stop working. A bearer-only client changing a password must sign in again. A 401 clears browser token/workspace state and returns to login. Failed mutations are not automatically replayed after authentication failure.

Schedule `python manage.py purge_access_grants` periodically to remove expired receipts; active receipts/logins remain intact. This is separate from the existing replay-body cleanup command.

## Setup and contract

Install updated requirements and apply authentication migration 0003_accessgrant before running this revision. Existing Owner/accounts are retained. Use a database backup before applying migrations to an existing installation.

The JWT-only stage added 48 paths and 75 operations, including the versioned login alias, session-token endpoint and exact `/health` route. That stage had seven public and 68 protected operations. The subsequent recovery feature brings the current contract to 50 paths/77 operations (nine public, 68 protected); see PASSWORD-RECOVERY.md. Existing `/api/v1/health` remains unchanged. Swagger advertises bearerAuth alongside cookieAuth; token renewal advertises cookieAuth only. Copy the login access_token into Swagger Authorize to demonstrate a protected call.

No live provider integration, hosted site, production deployment or successful GitHub run of these changes at the time of the local validation is claimed. The workflow now includes integration/submission branch pushes and the JWT browser regression. Public deployment after tests on main remains separate work.

## Verification

Regression coverage is in backend/authentication/tests/test_jwt.py and frontend/tests/jwt.spec.js. Backend coverage includes cookie-free reads/writes, roles, current-role changes, invalid signatures/algorithms/claims/expiry, CSRF bootstrap, session-only renewal, cookie/bearer logout, password rotation and session/grant revocation. The browser regression inspects actual outgoing bearer headers, memory-only storage, reload renewal and post-logout rejection.

Executed on 20 November 2026 using isolated synthetic accounts/data:

- Full SQLite regression with normal configured hashing: 322 discovered, 320 passed, two PostgreSQL-only skips; the two subsequently added JWT tests also passed separately with normal hashing.
- Fresh complete run after final backend edits with test-only MD5PasswordHasher: 324 discovered, 322 passed, two PostgreSQL-only skips. Production hashing remains unchanged.
- Static/runtime schema equality, warning-free runtime generation, Redocly lint, Django system checks and migration drift checks passed.
- Frontend lint and production build passed. The final Playwright run passed all five stories: JWT login/reload/logout and memory-only token storage, modal focus, password validation/rotation with a deliberately delayed old-token rejection, Owner/Admin/Staff hierarchy, and expired-session workspace clearing.
- An initial password-change browser regression exposed a stale background JWT rejection during rotation. The client now coordinates pending credentials, renews once and retries only the obsolete read; mutations are never replayed for this purpose. The password browser story deliberately delays an old-token 401 until after successful rotation.
- The browser download initially failed certificate validation; using Node's system trust store resolved it without disabling TLS verification. The optional local formatter was unavailable under Windows application-control policy; formatting is not counted as validation.

Local existing SQLite data was backed up privately before migration 0003_accessgrant; existing Owner/accounts were retained. Disposable validation databases and browser outputs are ignored by Git. No PostgreSQL rerun, public deployment, external gateway call or hosted GitHub Actions run was performed for this work. Historical evidence in VERIFICATION-RESULTS.md describes the prior revision.
