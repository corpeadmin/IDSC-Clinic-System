# PR title

Complete clinic website integration, account roles and one-time Owner setup

# Description

The clean repository had a verified backend but a starter frontend; the legacy interface simulated credentials and local record changes. This branch connects the recovered clinic layout to Django sessions/CSRF and the Clinic API, including records, consultations, statuses, dispensing/rollback, reports and account management.

Fresh installations register exactly one Owner and open Dashboard automatically. Later visits show shared login. Owner manages Admins/Staff; Admin manages Staff; Staff uses clinic features without administration. Admin capacity is five including inactive accounts; Staff pages contain at most ten accounts. Settings supports verified username/password changes and light/dark theme.

Registrar lookup/status refresh, inactive-student creation restrictions, Owner mock workspaces, selected/all restocks with fulfillment, notifications and Owner/Admin clinical/history deletion are implemented. Visible record numbers are consecutive while API IDs stay stable. History deletion does not restore stock.

The original 45-operation baseline was extended to 45 paths/72 operations (5 public/67 protected). Tests were retained and adjusted where role/deletion policy intentionally changed. Backend suite now contains 273 tests. See [CURRENT-VALIDATION.md](CURRENT-VALIDATION.md) for exact latest checks, faster-hasher test conditions and historical browser/Postman scope. [CONSOLIDATION-AUDIT.md](CONSOLIDATION-AUDIT.md) records branch selection.

Accounts/Owner registration persist in Django's database. Clinic and external mock business data remains in process memory and resets on restart. Optional empty mock startup is supported. Real external adapters and durable Clinic storage remain future work; see [REAL-SYSTEM-INTEGRATION.md](REAL-SYSTEM-INTEGRATION.md). Use a reviewed PR and teammate approval before merging main.
