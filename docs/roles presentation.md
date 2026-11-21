# Roles Presentation

This document describes the work represented by each project role in the verified IDSC Clinic Management System (`e67f8f2`).

## Frontend Developer

The frontend provides a React interface, built with Vite, for student lookup, health records, consultations, health statuses, medicine stock, dispensing, reports, and account management. It displays actions appropriate to the signed-in role and provides loading, empty, and error states. Reusable controls and dialogs keep forms consistent across the application. The interface also supports light and dark themes, responsive layouts, and keyboard focus in dialogs.

A shared API client sends session cookies, obtains CSRF tokens before write requests, and reuses submission keys when identical failed requests are retried within the retry window. When a session expires, the interface clears the workspace and returns the user to login. The backend enforces access permissions independently of the interface.

**Implementation:** [Application workflows](../frontend/src/App.jsx), [shared controls](../frontend/src/ClinicUI.jsx), and [API client](../frontend/src/api.js).

## Backend Developer

The Django REST Framework API authenticates sessions, validates input, and enforces Owner, Admin, and Staff permissions. It supports first-Owner registration, account administration, and clinical workflows. The service layer applies business rules, such as blocking new clinical activity for inactive students while preserving their history. The repository layer supports persistent clinical storage on SQLite or PostgreSQL in database mode.

For dispensing, the service checks student eligibility, requests a stock deduction, and records the Inventory transaction reference. Rollback uses that reference to return stock; deleting dispensing history does not return stock. The optional durable mock Inventory preserves stock, transactions, restocks, and notifications across restarts. An uncertain stock operation can block retries and be flagged for manual review. Registrar and Inventory remain simulated in this version.

**Implementation:** [Role permissions](../backend/authentication/permissions.py), [clinic services](../backend/clinic/services/clinic.py), [persistent repository](../backend/clinic/data/persistent.py), and [durable Inventory](../backend/clinic/services/durable_inventory.py).

## Documenter

The project documentation explains how to configure and run Django and React, apply database migrations, and register the first Owner. The architecture and data model define which records belong to Clinic, Registrar, and Inventory. The API reference and OpenAPI schema describe endpoints, inputs, responses, and access requirements. These materials provide a basis for reviewing the real Inventory team's API before connecting it.

The verification report records test results, skips, and known limitations. For the verified revision, it records 308 PostgreSQL backend tests passed, 306 SQLite backend tests passed with two PostgreSQL-only skips, and 13 browser scenarios passed. Newman completed 173 requests and 190 assertions with no failures. The documentation also covers backup and restore procedures and provides a repeatable demonstration using test data.

**Deliverables:** [Setup guide](../SETUP.md), [architecture](architecture.md), [API reference](../API.md), [verification report](VERIFICATION-RESULTS.md), [backup and restore guide](BACKUP-RESTORE.md), and [demo guide](FINAL-DEMO.md).
