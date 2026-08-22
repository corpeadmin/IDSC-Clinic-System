# IDSC Clinic System — Developer Setup Guide

This guide provides step-by-step instructions for installing, configuring, running, and verifying the **IDSC Clinic System** in a local development environment.

The project consists of:

* **Frontend:** React + Vite
* **Backend:** Django + Django REST Framework
* **Database:** PostgreSQL
* **Database Runtime:** Docker

> [!IMPORTANT]
> **PostgreSQL and Django have different responsibilities.**
>
> * **Docker** runs the PostgreSQL database server.
> * **PostgreSQL** provides the `clinic_db` database.
> * **Django migrations** create and update the database tables.
>
> Developers **do not manually create the application tables with SQL**.

---

## 1. Prerequisites

Ensure the following tools are installed:

| Tool               | Recommended Version | Purpose                       |
| :----------------- | :------------------ | :---------------------------- |
| **Git**            | `2.x+`              | Version control               |
| **Python**         | `3.10+`             | Backend runtime               |
| **Docker Desktop** | Latest              | Runs the PostgreSQL container |
| **Node.js**        | `18+`               | Frontend runtime              |
| **npm**            | `9+`                | Frontend package management   |

---

## 2. Get the Project

Clone the repository into your preferred workspace:

```powershell
git clone <repository-url> "IDSC Clinic System"
cd "IDSC Clinic System"
```

All commands in this guide assume you are working from the project root unless otherwise specified.

---

# 3. Start Docker Desktop

Launch **Docker Desktop** and make sure the Docker daemon is running.

Verify Docker is available:

```powershell
docker --version
```

You should receive a Docker version without a connection error.

---

# 4. PostgreSQL Setup

The project uses PostgreSQL through Docker so that developers can use a consistent database environment.

### How the database setup works

The setup follows this flow:

```text
Docker Desktop
      ↓
clinic-postgres container
      ↓
PostgreSQL server
      ↓
clinic_db database
      ↓
Django migrations
      ↓
Application + Django tables
```

### Important

You **do not manually create** tables such as:

* `students`
* `health_records`
* `auth_user`
* other Django-managed tables

Django creates and updates these tables through migrations.

---

## 4.1 First-Time Setup — Create the PostgreSQL Container

Run this command **only if the `clinic-postgres` container does not already exist**:

```powershell
docker run --name clinic-postgres -e POSTGRES_DB=clinic_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16-alpine
```

This command:

* Downloads the `postgres:16-alpine` image if it is not already available.
* Creates the container named `clinic-postgres`.
* Creates the PostgreSQL database `clinic_db`.
* Creates the PostgreSQL user `postgres`.
* Sets the development password to `postgres`.
* Exposes PostgreSQL on `localhost:5432`.
* Starts PostgreSQL in the background.

> [!IMPORTANT]
> `docker run` creates a **new container**. It should normally only be used during the initial setup.

After the container has been created, do **not** run the `docker run` command again.

---

## 4.2 Returning Developer — Start the Existing Container

If `clinic-postgres` already exists, start it with:

```powershell
docker start clinic-postgres
```

Check that it is running:

```powershell
docker ps
```

You should see `clinic-postgres` in the list of running containers.

---

## 4.3 PostgreSQL Container Management

Useful commands:

**Start:**

```powershell
docker start clinic-postgres
```

**Stop:**

```powershell
docker stop clinic-postgres
```

**Restart:**

```powershell
docker restart clinic-postgres
```

**Check running containers:**

```powershell
docker ps
```

**Check all containers:**

```powershell
docker ps -a
```

**View PostgreSQL logs:**

```powershell
docker logs clinic-postgres
```

---

# 5. Backend Virtual Environment

Navigate to the backend directory:

```powershell
cd backend
```

Create the virtual environment if one does not already exist:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell reports an execution-policy error, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\venv\Scripts\Activate.ps1
```

A successful activation should show `(venv)` in the terminal prompt.

---

# 6. Install Backend Dependencies

With the virtual environment activated and while inside the `backend` directory:

```powershell
pip install -r requirements.txt
```

The project's backend dependencies include:

* Django
* Django REST Framework
* django-cors-headers
* psycopg
* python-dotenv

The exact versions are controlled by `requirements.txt`.

> [!NOTE]
> `requirements.txt` is the source of truth for the project's Python dependencies. Do not manually install packages unless required by the project.

---

# 7. Environment Configuration

The Django backend reads database and application settings from:

```text
backend/.env
```

If the project provides an environment template, copy it:

```powershell
Copy-Item .env.example .env
```

Then open `backend/.env` and verify the database configuration.

Example development configuration:

```ini
SECRET_KEY=<your-development-secret-key>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=clinic_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

> [!IMPORTANT]
> Do not commit `.env` files containing secrets or credentials to Git.
>
> The values above are intended for local development only.

---

# 8. Database Migrations

This is the step that creates the Django database schema.

From the `backend` directory, run:

```powershell
python manage.py migrate
```

Django will create the tables required by:

* Django authentication
* Django admin
* Django sessions
* Content types
* The clinic application

### Important distinction

You do **not** need to manually create:

```text
students
health_records
auth_user
django_session
...
```

Django migrations handle these tables.

To see the migrations available and their status:

```powershell
python manage.py showmigrations
```

---

# 9. Database Inspection

You can inspect PostgreSQL directly through Docker without installing pgAdmin.

Connect to PostgreSQL:

```powershell
docker exec -it clinic-postgres psql -U postgres -d clinic_db
```

Inside `psql`, useful commands include:

### List tables

```sql
\dt
```

### Inspect students

```sql
\d students
```

### Inspect health records

```sql
\d health_records
```

### Query students

```sql
SELECT * FROM students;
```

### Query health records

```sql
SELECT * FROM health_records;
```

### Exit PostgreSQL

```sql
\q
```

> [!NOTE]
> Database inspection is optional. Normal development should be performed through the Django application, models, serializers, and API rather than manually modifying database tables.

---

# 10. Student ID Behavior

The `student_id` field is generated automatically.

### Creating a student

When creating a student through the API, **do not provide `student_id`**.

Example:

```json
{
    "first_name": "Juan",
    "last_name": "Dela Cruz"
}
```

Django/PostgreSQL generates the ID automatically.

For example:

```text
student_id = 1
```

The next student may receive:

```text
student_id = 2
```

### Creating a Health Record

When creating a health record, use the generated `student_id` of the student the record belongs to.

For example:

```json
{
    "student_id": 1
}
```

The same principle applies to `health_id`: it is generated automatically and should not normally be supplied manually.

> [!IMPORTANT]
> **Do not manually assign IDs in API requests unless the API documentation specifically requires it.**

---

# 11. Run Automated Tests

Run the backend test suite:

```powershell
python manage.py test clinic
```

The test suite verifies the application's models, serializers, endpoints, and database behavior.

A successful run should end with:

```text
OK
```

The exact number of tests and execution time may change as the project develops, so the current test count should not be treated as a permanent value.

---

# 12. Create a Django Admin Superuser

Creating a Django admin account is optional.

To create one:

```powershell
python manage.py createsuperuser
```

Follow the prompts to enter the username, email address, and password.

The Django Admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

---

# 13. Start the Backend

From the `backend` directory:

```powershell
python manage.py runserver 8000
```

The backend should now be available at:

```text
http://127.0.0.1:8000/
```

Important endpoints include:

| Endpoint               | Purpose            |
| :--------------------- | :----------------- |
| `/`                    | API root/discovery |
| `/api/students/`       | Students API       |
| `/api/health-records/` | Health Records API |
| `/admin/`              | Django Admin       |

---

# 14. Frontend Setup

Open a **separate terminal window**.

Navigate to the frontend:

```powershell
cd frontend
```

Install the frontend dependencies:

```powershell
npm install
```

Start the Vite development server:

```powershell
npm run dev
```

The frontend should be available at:

```text
http://localhost:5173
```

---

# 15. Normal Development Workflow

Once the project has already been set up, the normal workflow is:

### Terminal 1 — PostgreSQL

```powershell
docker start clinic-postgres
```

### Terminal 2 — Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 8000
```

### Terminal 3 — Frontend

```powershell
cd frontend
npm run dev
```

You normally **do not need to recreate the PostgreSQL container**.

You only need to run `docker run` again if the existing container has been intentionally removed.

---

# 16. Verification Checklist

Use this checklist to confirm that the development environment is working:

* [ ] Docker Desktop is running.
* [ ] `clinic-postgres` exists.
* [ ] `clinic-postgres` is running.
* [ ] PostgreSQL is available on port `5432`.
* [ ] `clinic_db` exists.
* [ ] `backend/.env` is configured.
* [ ] Python virtual environment is activated.
* [ ] Backend dependencies are installed.
* [ ] Django migrations complete successfully.
* [ ] `students` table exists.
* [ ] `health_records` table exists.
* [ ] Backend tests pass.
* [ ] Django backend runs on port `8000`.
* [ ] API root responds.
* [ ] Frontend dependencies are installed.
* [ ] Vite frontend runs on port `5173`.

---

# 17. Troubleshooting

## Container Name Already Exists

### Error

```text
The container name "/clinic-postgres" is already in use
```

### Solution

The container has already been created.

Do not run `docker run` again.

Start the existing container:

```powershell
docker start clinic-postgres
```

---

## PostgreSQL Port Already in Use

### Error

```text
Error: Port 5432 is already allocated
```

Another PostgreSQL instance or container is already using port `5432`.

Check running containers:

```powershell
docker ps
```

If another container is using the port, stop it if appropriate:

```powershell
docker stop <container_id>
```

You can also check whether a local PostgreSQL service is using the port.

---

## Django Port Already in Use

### Error

```text
Error: That port is already in use
```

Run Django on another port:

```powershell
python manage.py runserver 8080
```

---

## Migration Problems

Check migration status:

```powershell
python manage.py showmigrations
```

Check whether model changes require migrations:

```powershell
python manage.py makemigrations --check
```

If migrations are required because models were intentionally changed, create them with:

```powershell
python manage.py makemigrations
```

Then apply them:

```powershell
python manage.py migrate
```

> [!IMPORTANT]
> Do not manually modify the PostgreSQL schema to fix a Django migration issue. Resolve the issue through Django's migration system.

---

## PostgreSQL Connection Error

If Django cannot connect to PostgreSQL, verify:

1. Docker Desktop is running.
2. `clinic-postgres` is running.
3. PostgreSQL is listening on port `5432`.
4. `clinic_db` exists.
5. The database credentials in `.env` match the PostgreSQL container.
6. `DB_HOST` is set to `localhost`.
7. `DB_PORT` is set to `5432`.

Check the container:

```powershell
docker ps
```

Check its logs:

```powershell
docker logs clinic-postgres
```

---

# 18. Key Development Rules

Keep these rules in mind when working on the project:

1. **Do not manually create database tables.**
2. **Do not manually assign `student_id` when creating students.**
3. **Do not manually assign `health_id` unless explicitly required.**
4. **Use Django migrations for database schema changes.**
5. **Use the existing `clinic-postgres` container instead of creating another one.**
6. **Keep local credentials and secrets out of Git.**
7. **Use the API/models rather than manually modifying database records during normal development.**

The intended architecture is:

```text
React / Vite
     │
     │ HTTP API
     ▼
Django / DRF
     │
     │ Django ORM
     ▼
PostgreSQL
     │
     │
     ▼
Docker Container
```

This separation keeps the development environment consistent and prevents developers from accidentally creating conflicting database schemas or containers.
