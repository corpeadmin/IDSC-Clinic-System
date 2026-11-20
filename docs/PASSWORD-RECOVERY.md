# Forgotten-password recovery and Gmail setup

The login page now has an active Forgot password button. It opens an email dialog. An active account with a usable password receives a 30-minute reset link at the address already saved on that account. The link opens a new-password/confirmation form. Success revokes all of that account's sessions and JWT receipts and requires a fresh login. Owner, Admin and Staff can recover credentials without changing their roles.

Sender and recipient are different settings: the sender is the Gmail account authorized to send system notifications; the recipient is the email saved on the Clinic user's account. A sender does not need to be that user's Gmail. Valid non-Gmail recovery addresses also work. Unknown, inactive or unusable accounts return HTTP 404 with a visible email-not-found message. The sender address is never automatically assigned as a recovery recipient.

## Configure a sender you own

Use a Gmail account controlled by the group, preferably a dedicated Clinic notifications account. For a short school demonstration, an existing member's account may be used with their agreement. An invented address or one owned by somebody else cannot send these messages.

1. The Gmail owner enables 2-Step Verification.
2. The owner creates an App Password for this application. Use [Google's official instructions](https://support.google.com/accounts/answer/185833). Some school/work accounts or security policies do not allow App Passwords; use an eligible account or an approved mail provider instead.
3. Copy the configuration keys from [email.env.example](../backend/email.env.example) into private backend/.env. Set EMAIL_HOST_USER and DEFAULT_FROM_EMAIL to the owned sender Gmail. Set EMAIL_HOST_PASSWORD to the App Password, not the normal Gmail password. Do not paste secrets into chat or commit them.
4. Set PASSWORD_RESET_FRONTEND_URL to the real website origin. Locally use http://localhost:5173 or http://127.0.0.1:5173 consistently with the browser. Production must use HTTPS. Links never use untrusted request Host values.
5. Restart Django so it reloads configuration. Inside backend run `python manage.py check_reset_email`. SMTP success verifies connection/authentication only, not final inbox placement.
6. Confirm the recovery recipient email is saved on the intended account. Owner/Admin can edit managed Staff emails; Owner edits Admin emails. An authorized Owner can maintain their own email in Django administration. Account email ownership should be established before using it for recovery.
7. Use Forgot password, then check the recipient inbox and spam folder. Test the link, new login, old-password rejection and one-time use. Inbox delivery is not claimed until this is performed with real configured credentials.

Gmail uses smtp.gmail.com, port 587 with STARTTLS; see [Google's SMTP documentation](https://developers.google.com/workspace/gmail/imap/imap-smtp). The Compose backend accepts the same private SMTP environment values. Backend/.env is excluded from Docker images and Git; supply container values through the deployment environment. Never print a credential-expanded Compose configuration publicly.

## Development and tests

With no SMTP configured and DEBUG=True, the default file email backend writes private messages under .runtime/reset-emails. This is a local test outbox, not Gmail delivery. Unknown or ineligible addresses return 404 before contacting the mail transport. For eligible accounts, missing SMTP credentials, connection failures and message submission failures return 503. Success is returned only after the transport accepts the message; final inbox placement still requires verification. Logs contain only the exception class, never recipient/link/password/body.

Private Gmail SMTP connection and authentication were verified on 20 November 2026. A real password-reset request was subsequently accepted by Gmail SMTP. The user confirmed receipt and a working reset on 20 November 2026. Credentials remain in the ignored private environment file.

## Backend API and safeguards

- POST /api/auth/password/reset/: JSON email. Returns 200 after message submission, 404 when no active recoverable account matches, 400 for malformed input, and 503 for mail-service failure. Applies CSRF and rate limits. The requested email-not-found feedback reveals whether an eligible account exists; tokens are never returned in the API response.
- POST /api/auth/password/reset/confirm/: JSON uid/token/new_password/confirm_password. Validates the link under an account lock, applies Django password validators and non-reuse, updates the hash and revokes sessions/JWTs. Invalid/expired/reused links return 400. Does not automatically sign in.
- Both endpoints are public but CSRF-protected and rate-limited to a combined ten attempts/hour per direct peer IP. The current cache is process-local; configure shared limiting/trusted proxy handling before scaling.
- Django PasswordResetTokenGenerator binds the link to password, email and login state. Password changes, successful use, changed email or expiry invalidate it. Deactivated/unusable accounts cannot reset. Concurrent consumption is serialized on SQLite/PostgreSQL through the existing account database.
- Email links carry the credential in a URL fragment, not in a server path/query. The website reads it into memory and removes it from the address bar. Reopen the email link after reloading an unfinished reset page. Do not share links or include them in screenshots/logs.
- Email recovery does not bypass Owner uniqueness, Admin limits or clinic role checks. It cannot reactivate a deactivated account.

The OpenAPI inventory is now 50 paths/77 operations (9 public, 68 protected). Session login, JWT login, logged-in password changes and prior business operations remain available.

## Verification

Backend tests cover email contents/origin, email-not-found responses, inactive/unusable accounts, CSRF, validation, expiration, tampering, non-reuse, session/JWT revocation, Owner recovery, SMTP failures and rate limits. The browser story uses an explicitly isolated file outbox and disposable Staff account. It does not use real Gmail credentials. Executed validation on 20 November 2026:

- Full SQLite suite using a test-only faster hasher: 342 discovered, 340 passed, two PostgreSQL-only skips. Production hashing is unchanged.
- All 18 recovery tests passed separately with normal configured hashing, including a mocked Gmail SMTP TLS/authentication transport test.
- Browser recovery story passed: enabled button/modal focus, visible unknown-email error, email-outbox generation/decoding, same-tab reset navigation, matching-password validation, successful reset, old JWT/password rejection, new login, and safe invalid/reused-link feedback.
- JWT and modal-focus browser regressions also passed. Desktop/mobile visual inspection completed; mobile dialog had no horizontal overflow.
- Frontend lint/build, schema generation/equality, static Redocly lint, configuration and migration checks passed.
- Early browser checks exposed same-tab fragment routing and inconsistent field-error shapes; both were fixed. The test email reader was updated to decode quoted-printable MIME, as a real inbox does.

Real Gmail SMTP authentication and message submission succeeded. After registering a fresh Owner with a valid recovery address, the user confirmed that the email-based reset worked on 20 November 2026. Inbox receipt and the manual reset are user-confirmed; automated tests separately verify old-password/JWT rejection and single-use links. No recipient address, reset token or credentials are recorded here.
