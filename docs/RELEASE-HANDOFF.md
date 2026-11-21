# Production release handoff

Verified 21 November 2026. Public school demo: https://idsc-clinic-management.vercel.app. Swagger: https://idsc-clinic-management.vercel.app/docs. Backend: https://idsc-clinic-api.onrender.com.

## Completed

The initial manual release used tested commit 4645e34. The database uses certificate and hostname verification. Initial Owner bootstrap values have been removed from Render; configuration restart succeeded and the existing Owner login passed. The recipient confirmed the Brevo reset email arrived and opens the hosted reset form. Completed reset redemption remains unverified.

## Repository administrator steps

The connected GitHub account has push access but not administrator or maintain access. It cannot finish the protected production setup. An administrator must configure it; no one should send credentials through chat or commit them.

1. Review the integration/final-jwt PR and its CI before merging. Do not change main directly.
2. Create the production GitHub environment. Restrict deployment branches to main and add appropriate required reviewers if the repository plan supports them. If unavailable, resolve an equivalent release approval control before enabling unattended deployment.
3. Add these production environment variables:

| Variable | Exact target |
| --- | --- |
| RENDER_SERVICE_ID | srv-dc0hvj3m8hqs73ej4cd0 |
| VERCEL_ORG_ID | team_HdARo0iOrh1BmVYQhyJcTrUC |
| VERCEL_PROJECT_ID | prj_6UiTp5itGeTnNlSwnk8tU3ULwD0h |
| CLINIC_BACKEND_ORIGIN | https://idsc-clinic-api.onrender.com |
| CLINIC_PUBLIC_ORIGIN | https://idsc-clinic-management.vercel.app |

4. Enter environment secrets privately: RENDER_API_KEY, VERCEL_TOKEN and VERCEL_AUTOMATION_BYPASS_SECRET for protected staged deployment checks. Use the appropriate hosting account and intended project permissions. Vercel CLI created a project automation bypass during staging verification; do not create unrelated access or expose its value. Database credentials, SECRET_KEY and BREVO_API_KEY remain in Render, not GitHub variables or the frontend.
5. Keep Render Auto-Deploy Off. After the PR is approved and ready to merge, set Render's service branch to main. The release script checks that branch, repository and auto-deploy setting before requesting a deployment.
6. Set the repository variable CLINIC_DEPLOY_ENABLED=true only after those settings are checked, then merge the reviewed PR. The push to main must finish all quality jobs before release starts. Approve the exact commit if the production environment requires review.
7. Confirm the release job deploys that exact main SHA on Render, stages the Vercel frontend, passes staging checks, promotes it and passes public checks. Record the successful Actions URL. Until that actually happens, automated deployment on push to main is prepared but unverified.

See CLOUD-RELEASE.md for configuration, cold-start limits and rollback cautions. Removing bootstrap settings did not delete or reset the Owner account. Do not re-import an old private env file without removing INITIAL_OWNER_* first.

## External provider handoff

A real Registrar lookup is the smallest sufficient real integration. Supply the other group's repository, agreed gateway HTTPS origin, versioned OpenAPI path, server-side authentication method, synthetic test student ID, response example, ACTIVE/GRADUATED/DROPPED_OUT mappings and agreed timeout/offline behavior. Record the agreement with its date/contact in the project's integration agreement log. Credentials must be entered privately.

Inventory integration additionally needs transaction IDs, idempotency and reconciliation rules, stock units, request/delivery transitions and reversal semantics. No real endpoint or payload is assumed; current Registrar/Inventory are mocks. See REAL-SYSTEM-INTEGRATION.md.
