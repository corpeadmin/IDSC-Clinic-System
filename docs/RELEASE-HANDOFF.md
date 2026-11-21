# Production release handoff

Verified 21 November 2026. Public school demo: https://idsc-clinic-management.vercel.app. Swagger: https://idsc-clinic-management.vercel.app/docs. Backend: https://idsc-clinic-api.onrender.com.

## Completed

The initial manual release used tested commit 4645e34. The database uses certificate and hostname verification. Initial Owner bootstrap values have been removed from Render; configuration restart succeeded and the existing Owner login passed. The recipient confirmed the Brevo reset email arrived and opens the hosted reset form. Completed reset redemption remains unverified.

## Current repository and release setup

The repository is now https://github.com/microwaveTuesday/IDSC-Clinic-System. Ownership transfer is verified: microwaveTuesday has administrator access. PR #4 was merged as 23cf46c and its main quality run passed; production release was skipped because deployment is not enabled.

The production environment now requires microwaveTuesday review, restricts deployment to the main branch, and disallows administrator bypass. Prevent self-review stays off so the sole configured operator can approve their own release. All five variables below are saved. Deployment secrets are not yet configured; enter them directly in GitHub, never through chat. Render source is updated to the transferred repository and main branch, while Docker, the existing Dockerfile path and Auto-Deploy Off are preserved.

1. Review the ownership/release follow-up PR and its CI before merging. PR #4 is already merged; do not recreate it or change main directly.
2. Keep the configured production protection rules: main only, required owner review and no administrator bypass.
3. Keep these configured production environment variables:

| Variable | Exact target |
| --- | --- |
| RENDER_SERVICE_ID | srv-dc0hvj3m8hqs73ej4cd0 |
| VERCEL_ORG_ID | team_HdARo0iOrh1BmVYQhyJcTrUC |
| VERCEL_PROJECT_ID | prj_6UiTp5itGeTnNlSwnk8tU3ULwD0h |
| CLINIC_BACKEND_ORIGIN | https://idsc-clinic-api.onrender.com |
| CLINIC_PUBLIC_ORIGIN | https://idsc-clinic-management.vercel.app |

4. Enter environment secrets privately: RENDER_API_KEY, VERCEL_TOKEN and VERCEL_AUTOMATION_BYPASS_SECRET for protected staged deployment checks. Use the appropriate hosting account and intended project permissions. Vercel CLI created a project automation bypass during staging verification; do not create unrelated access or expose its value. Database credentials, SECRET_KEY and BREVO_API_KEY remain in Render, not GitHub variables or the frontend.
5. Keep Render Auto-Deploy Off, the source at microwaveTuesday/IDSC-Clinic-System, and the branch at main. These are already configured. The release script verifies them before requesting a deployment.
6. Set the repository variable CLINIC_DEPLOY_ENABLED=true only after those settings are checked, then merge the reviewed PR. The push to main must finish all quality jobs before release starts. Approve the exact commit if the production environment requires review.
7. Confirm the release job deploys that exact main SHA on Render, stages the Vercel frontend, passes staging checks, promotes it and passes public checks. Record the successful Actions URL. Until that actually happens, automated deployment on push to main is prepared but unverified.

See CLOUD-RELEASE.md for configuration, cold-start limits and rollback cautions. Removing bootstrap settings did not delete or reset the Owner account. Do not re-import an old private env file without removing INITIAL_OWNER_* first.

## External provider handoff

A real Registrar lookup is the smallest sufficient real integration. Supply the other group's repository, agreed gateway HTTPS origin, versioned OpenAPI path, server-side authentication method, synthetic test student ID, response example, ACTIVE/GRADUATED/DROPPED_OUT mappings and agreed timeout/offline behavior. Record the agreement with its date/contact in the project's integration agreement log. Credentials must be entered privately.

Inventory integration additionally needs transaction IDs, idempotency and reconciliation rules, stock units, request/delivery transitions and reversal semantics. No real endpoint or payload is assumed; current Registrar/Inventory are mocks. See REAL-SYSTEM-INTEGRATION.md.

The partner groups were reported unfinished on 21 November 2026. Mock demonstrations remain available, but do not establish the required real gateway call. Real adapters can be added and redeployed when the verified contracts arrive.
