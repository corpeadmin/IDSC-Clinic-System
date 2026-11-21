# Cloud deployment plan

Status: cloud preparation implemented; hosted deployment is not yet verified. Follow [CLOUD-RELEASE.md](CLOUD-RELEASE.md) for the current free-hosting/email choice, private Owner provisioning and test-gated release workflow. The details below describe the earlier proposed topology.

| Layer | Platform | Responsibility |
| --- | --- | --- |
| Frontend | Vercel | Build and serve the React/Vite application |
| Backend | Render | Run Django and Gunicorn; enforce authentication, permissions, and clinic workflows |
| Database | Supabase | Host PostgreSQL for Django accounts, sessions, and clinic records |

Request path: **Browser → Vercel (/api) → Render (Django) → Supabase (PostgreSQL)**. Django remains responsible for user accounts and authorization. The browser does not connect to Supabase or need its keys.

1. **Supabase:** Create a separate staging project with synthetic data. Disable the Data API for this database if unused and verify clinic tables are not exposed to browser roles. Copy connection details from the Connect dashboard; use the session pooler on port 5432 if the backend needs IPv4. Require TLS and verify the certificate with the appropriate CA. Supply Render's `DB_ENGINE=django.db.backends.postgresql` and `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. The current settings read these individual variables, not `DATABASE_URL`; explicitly configure and verify PostgreSQL TLS before release. [Supabase connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres)

2. **Render:** Deploy the reviewed revision as a Python web service with root directory `backend`. Build with `python -m pip install -r requirements-deployment.txt`. Run `python manage.py migrate --noinput` as a release step before sending traffic (use a pre-deploy command if supported by the selected plan). Start with `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1`. Set `DEBUG=False`, `CLINIC_DATA_BACKEND=database`, a private `SECRET_KEY`, and explicit production hosts and trusted origins. Verify HTTPS proxy handling and secure cookies. Configure and test static serving separately if Django admin is needed. Complete first-Owner registration privately before granting public access. [Render Django guide](https://render.com/docs/deploy-django), [Render release steps](https://render.com/docs/deploys)

3. **Vercel:** Set the project root to `frontend`, install with `npm ci`, build with `npm run build`, and publish `dist`. Add a rewrite from `/api/:path*` to `https://<render-host>/api/:path*`; Vite's development proxy does not ship with the build. Keep API requests on the frontend origin, set Django's CSRF trusted origin to the exact Vercel URL, and verify forwarded host handling, cookies, and CSRF on real browser requests. Keep authenticated API responses out of shared caches. Store no database or Django secrets in frontend variables. [Vercel rewrites](https://vercel.com/docs/routing/rewrites)

4. **Demo data:** Registrar and Inventory are still mocks. Use one backend instance and worker while they are process-local. If durable mock Inventory is needed, set `INVENTORY_BACKEND=durable_mock` and put `MOCK_INVENTORY_DB` on an attached Render persistent disk. That ledger is separate from Supabase. Without the disk, use the disposable mock and expect stock to reset. [Render persistent disks](https://render.com/docs/disks)

5. **Release checks:** Verify API health, first-Owner setup, login/logout, role restrictions, a CSRF-protected write, and clinical data after a backend restart. If using durable mock Inventory, verify stock survives a restart and a rollback returns stock only once. Keep staging separate from real clinic data. Record deployed revisions and URLs, back up the database and any mock ledger, and test recovery before promoting the release. Reverting code does not undo database migrations.

See [local deployment](DEPLOYMENT.md), [backup and restore](BACKUP-RESTORE.md), and [verification results](VERIFICATION-RESULTS.md) for existing evidence.
