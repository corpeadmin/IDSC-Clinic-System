# Hosted release setup

Deployed 21 November 2026 from tested commit `4645e34` on `integration/final-jwt`. Public website: https://idsc-clinic-management.vercel.app; backend: https://idsc-clinic-api.onrender.com. Initial deployment was performed manually after all 12 quality jobs passed, not by a push to main. Main remains unchanged.

## Chosen school-demo topology

Browser -> Vercel same-origin routes -> Render Free Docker backend -> Supabase PostgreSQL. Password reset uses Brevo's HTTPS transactional API. Gmail SMTP remains available locally and was previously inbox-tested. The verified Brevo sender accepted a real reset request from the hosted API (HTTP 200); the user confirmed inbox receipt and that the hosted reset form opens. Completed hosted password reset remains unverified.

Render Free blocks outbound SMTP on 465/587, has an ephemeral filesystem, and sleeps after 15 minutes of inactivity. Cold starts can take about a minute. Do not put Clinic data or a durable mock Inventory ledger on its local disk. This profile persists Clinic records/accounts in PostgreSQL; Registrar and Inventory remain explicitly process-local mocks. Run one instance/worker. Free hosting is suitable for the synthetic school demo; immediate availability and institutional production operation are not established. See [Render limits](https://render.com/docs/free).

## Configure the database

Use a separate Clinic project on the Supabase Free plan; do not modify another group's database. Disable the project's Data API if it is not needed. If it must stay enabled, keep Django tables outside its exposed schemas or deny browser roles access with appropriate RLS and grants. Django owns authentication and migrations; no Supabase browser key is needed.

Use the Connect dashboard's PostgreSQL session pooler (IPv4-compatible, port 5432) when needed. Enter the exact DB host/user/password/database in Render privately. Set `DB_SSLMODE=verify-full`. If the provider requires its own CA, upload the CA as a Render secret file and set `DB_SSLROOTCERT` to that file path. Do not weaken certificate verification to fix a failed connection. Validate a real connection before claiming readiness. [Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres)

## Configure the Render backend

- Repository: `https://github.com/microwaveTuesday/IDSC-Clinic-System` (transferred from corpeadmin on 21 November 2026).
- Initial staging branch was `integration/final-jwt`; PR #4 is now merged and Render targets `main`, with Auto-Deploy Off.
- Runtime: Docker; Dockerfile: `deploy/Dockerfile.backend`; build context: repository root.
- Compute: Free; one worker/instance. Health-check path: `/api/auth/setup/` (checks the account database).
- Set private environment values from [cloud.env.example](../deploy/cloud.env.example). Replace example domains with the actual Render and stable Vercel domains.
- Set `SERVE_STATIC=True`; collected Django admin assets are served by WhiteNoise.
- Keep `REQUIRE_OWNER_BEFORE_SERVING=True`. Enter `INITIAL_OWNER_USERNAME`, `INITIAL_OWNER_PASSWORD` and a valid `INITIAL_OWNER_EMAIL` privately. Startup migrates the database and provisions the first Owner before opening the listener. Existing Owners are never overwritten. Remove those three initial credentials from hosting after confirming login.
- Configure `SECRET_KEY` privately with at least 50 random characters. Do not copy development keys or local account/database files into hosting.
- Disable Render's independent auto-deploy before enabling the GitHub release job. The workflow deploys a specific tested commit and verifies that same commit is live.

Gunicorn uses Render's `PORT` (8000 outside hosted environments). The existing private Compose/Caddy setup remains available for isolated deployment tests. Render supplies public HTTPS; Caddy's private test certificate is not used there.

## Configure email on the free backend

Create a Brevo Free account, activate transactional sending and verify an address you control. Set `EMAIL_BACKEND=authentication.email_backends.BrevoEmailBackend`, a private `BREVO_API_KEY`, and `DEFAULT_FROM_EMAIL` to the verified sender. Set `PASSWORD_RESET_FRONTEND_URL` to the stable public Vercel origin.

Brevo currently offers 300 messages/day on Free. With a free-address sender such as Gmail, Brevo may replace the sender address with a compliant provider address; recipients may therefore see a different From address. Domain authentication is preferable when an owned domain is available. Account activation/sender approval and inbox placement must be verified. [Plans](https://help.brevo.com/hc/en-us/articles/208589409-About-Brevo-s-pricing-plans), [sender requirements](https://help.brevo.com/hc/en-us/articles/14925263522578-Comply-with-Gmail-Yahoo-and-Microsoft-s-requirements-for-email-senders)

`python manage.py check_reset_email` checks a read-only transactional statistics endpoint without sending mail, so its diagnostic does not require account-wide permissions. Use a Restricted Brevo key with Transactional email set to All (Read cannot send), leaving unrelated services at None. Provider errors return the existing 503 response; unknown Clinic emails still return 404. The API key, reset links, email bodies and recipient addresses are not printed. Sending uses verified HTTPS, fixed provider URLs, a timeout and no redirects or automatic retries.

## Configure Vercel and GitHub deployment

Use a Vercel Hobby project for this noncommercial school demo. Record its org and project IDs and intended stable domain. Keep automatic Git deployments off when using the CI-controlled production release, so they cannot bypass tests. Configure the `production` GitHub environment for the reviewed `main` branch and appropriate reviewers.

Set these GitHub **variables** in that environment:

| Variable | Value |
| --- | --- |
| `RENDER_SERVICE_ID` | Intended backend service ID |
| `VERCEL_ORG_ID` | Intended Vercel owner/team ID |
| `VERCEL_PROJECT_ID` | Intended frontend project ID |
| `CLINIC_BACKEND_ORIGIN` | Exact HTTPS Render origin |
| `CLINIC_PUBLIC_ORIGIN` | Exact stable HTTPS frontend origin |

Set `CLINIC_DEPLOY_ENABLED=true` as a repository variable only after configuration is verified. Set these GitHub **environment secrets** privately: `RENDER_API_KEY`, `VERCEL_TOKEN`, and, if staging deployment protection is enabled, `VERCEL_AUTOMATION_BYPASS_SECRET`. These deployment credentials are separate from the database/Brevo secrets stored only in the backend hosting environment.

The quality workflow now runs on pushes to `main` as well as integration/submission branches. The release job runs only on an enabled push to `main`, after every backend/database, contract, frontend, dependency, container, Postman and browser job succeeds. No deployment credentials are exposed to PR jobs.

Release sequence:

1. Build the static React application without production credentials.
2. `scripts/prepare_cloud_frontend.py` packages `frontend/dist` into ignored `.vercel/output` using Build Output API v3. API, Swagger, health, admin and Django static routes go to the backend before the SPA fallback. API responses use `no-store`.
3. `scripts/deploy_render.py` checks the target repository, main branch and disabled auto-deploy, requests the exact tested SHA, and waits for that same SHA to be live. It stops on failure or timeout.
4. Pinned Vercel CLI stages the prebuilt frontend without assigning production domains.
5. Read-only HTTPS smoke checks verify the frontend, health, database-backed setup, closed Owner registration, no-store API, OpenAPI, Swagger and protected dashboard.
6. Promote the exact checked production deployment through the project-scoped REST API, verify the stable public domain is assigned to that exact deployment, and rerun checks against the stable public origin. The API avoids CLI account-profile lookups that project-scoped tokens cannot satisfy.

The staged checks do not prove authenticated browser writes, inbox delivery, provider integration or a database restart. Run those separately on the final public origin before submission. Code rollback does not undo migrations; back up the database before releases. If a backend update succeeds and frontend publication fails, investigate compatible rollback before retrying. [Render exact-commit deploys](https://api-docs.render.com/reference/create-deploy), [Vercel Build Output](https://vercel.com/docs/build-output-api), [Vercel CLI](https://vercel.com/docs/cli/deploy)

## Remaining real integration inputs

The minimum genuine provider call can be Registrar student lookup through the agreed gateway. Obtain the actual gateway HTTPS origin, OpenAPI/versioned lookup path, server-side authentication method, a synthetic test student ID, response examples and mappings for ACTIVE/GRADUATED/DROPPED_OUT, timeout/offline behavior and the other group's agreement contact. Record the agreement before implementing the adapter. No provider URL or contract is invented here.

For Inventory mutations also obtain idempotency-key rules, stable transaction IDs, stock-unit semantics, request/delivery state transitions and transaction-status lookup for uncertain outcomes. Keep mock and real ledgers separate. See [REAL-SYSTEM-INTEGRATION.md](REAL-SYSTEM-INTEGRATION.md). No real Registrar/Inventory call is implemented by this deployment preparation.

## Current release handoff

Temporary INITIAL_OWNER_* variables were removed from Render and a configuration restart retained the existing Owner. Exact non-secret production targets and administrator steps are in [RELEASE-HANDOFF.md](RELEASE-HANDOFF.md). The repository has since transferred to microwaveTuesday, which now has administrator access. The production environment, target variables and three deployment secrets are configured. The operator approved commit f43769b and all 13 jobs, including the complete production release, succeeded. See [RELEASE-EVIDENCE.md](RELEASE-EVIDENCE.md) for the exact run and independent checks.
