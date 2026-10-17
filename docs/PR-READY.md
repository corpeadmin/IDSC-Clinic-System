# PR title

Integrate clinic frontend with verified session API and consolidate legacy UI

# Description

The clean repository had a verified backend but a starter frontend; the strongest legacy interface used simulated credentials and browser-only record changes. This branch selectively reuses the clinic layout and connects it to the existing API, including health records, consultations, statuses, medicine dispensing and rollback, four reports, and administrator staff management.

Session cookies and CSRF remain enforced. Registrar students and Inventory medicine/stock remain read-only projections. The backend implementation, existing tests, static OpenAPI contract and Postman collection are preserved unchanged. Synced school documentation is untouched.

Branch selection and documentation conflicts are explained in `docs/CONSOLIDATION-AUDIT.md`. Reproduction and executed results are in `docs/INTEGRATION-VALIDATION.md`.

Validation: 167 Django tests; configuration/migration/schema checks; matching 29-path/45-operation schemas; both Redocly lints; Newman 45 requests and 46 assertions; frontend lint/build and dependency audit; browser clinical and account flows.

The verified runtime still uses process-memory business data and mock external services. Production requires durable storage and a same-origin API reverse proxy. Final visual sign-off, branch protection and teammate PR approval remain reviewer gates. Review and merge through a PR only.
