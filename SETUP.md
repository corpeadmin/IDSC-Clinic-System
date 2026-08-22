# IDSC Clinic System — Developer Setup Guide

This guide provides step-by-step instructions for installing, configuring, running, and verifying the **IDSC Clinic System** on a local development environment.

---

## 1. Prerequisites

Ensure the following tools are installed on your machine:

| Tool | Recommended Version | Purpose |
| :--- | :--- | :--- |
| **Git** | `2.x+` | Version control |
| **Python** | `3.14.x` (or `3.10+`) | Backend runtime |
| **Docker Desktop** | Latest (WSL2 / Windows backend) | Hosts PostgreSQL container |
| **Node.js & npm** | Node `18+` / npm `9+` | Frontend build and runtime |

---

## 2. Get the Project

Clone or open the repository into your preferred local workspace directory:

```powershell
git clone <repository-url> "IDSC Clinic System"
cd "IDSC Clinic System"
```

*(Note: You do not need to use a specific absolute path; all instructions below use relative commands from your project root).*

---

## 3. Start Docker Desktop

Launch **Docker Desktop** on your machine and confirm the Docker daemon is active.

Verify Docker CLI connectivity:
```powershell
docker --version
```

---

## 4. First-Time PostgreSQL Setup

The project uses a containerized PostgreSQL instance to ensure consistency across developer environments.

### Create the Database Container (Run Once)
Run the following command in PowerShell to create and start the `clinic-postgres` container:

```powershell
docker run --name clinic-postgres -e POSTGRES_DB=clinic_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16-alpine
```

### What this command does:
* Downloads the lightweight `postgres:16-alpine` image.
* Creates and names the container `clinic-postgres`.
* Initializes the default database: `clinic_db`.
* Sets default credentials: user `postgres`, password `postgres`.
* Maps port `5432` from inside the container to `localhost:5432`.
* Starts the PostgreSQL service detached in the background (`-d`).

> [!IMPORTANT]
> The `docker run` command is **only executed once** during initial setup. For subsequent development sessions, use `docker start clinic-postgres`.

---

## 5. Returning Developer Commands (Container Management)

Once the container exists, manage its lifecycle using these standard commands:

* **Start PostgreSQL container**:
  ```powershell
  docker start clinic-postgres
  ```
* **Stop PostgreSQL container**:
  ```powershell
  docker stop clinic-postgres
  ```
* **Restart PostgreSQL container**:
  ```powershell
  docker restart clinic-postgres
  ```
* **Check running containers**:
  ```powershell
  docker ps
  ```
* **Check all containers (including stopped)**:
  ```powershell
  docker ps -a
  ```
* **View PostgreSQL container logs**:
  ```powershell
  docker logs clinic-postgres
  ```

---

## 6. Python Virtual Environment

Navigate to the `backend` folder:

```powershell
cd backend
```

### Create Virtual Environment (if not already created)
```powershell
python -m venv venv
```

### Activate Virtual Environment (Windows PowerShell)
```powershell
.\venv\Scripts\Activate.ps1
```

*(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the activation script again).*

---

## 7. Install Backend Dependencies

With the virtual environment active inside the `backend` directory, install all dependencies:

```powershell
pip install -r requirements.txt
```

### Verified Packages Installed:
* `Django>=6.1,<6.2`
* `djangorestframework>=3.18.0,<3.19`
* `django-cors-headers>=4.9.0,<4.10`
* `psycopg[binary]>=3.3.4`
* `python-dotenv>=1.2.3`

---

## 8. Environment Configuration

The backend reads settings dynamically from `backend/.env`.

1. Copy the example environment template:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Verify the configuration values in `backend/.env`:
   ```ini
   SECRET_KEY=django-insecure-4uipb%r-hr+7aq+2g7xtu(a6gnf=0s-^ql!b6^=q=vi8g+2kz4
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

---

## 9. Database Migrations

> [!IMPORTANT]
> **Developers do NOT manually create tables with raw SQL.**
> PostgreSQL provides the database engine, and Django migrations manage the schema.

Apply migrations to initialize both Django's built-in framework tables and the clinic application tables:

```powershell
python manage.py migrate
```

### Expected Output:
```text
Operations to perform:
  Apply all migrations: admin, auth, clinic, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying clinic.0001_initial... OK
  Applying clinic.0002_alter_student_student_id... OK
  Applying sessions.0001_initial... OK
```

---

## 10. Verify PostgreSQL Database (using Docker CLI / psql)

You can inspect the database directly through the Docker CLI without needing pgAdmin:

### 1. Connect to PostgreSQL inside the container
```powershell
docker exec -it clinic-postgres psql -U postgres -d clinic_db
```

### 2. Useful inspection commands inside `psql`
* **List all tables**:
  ```sql
  \dt
  ```
* **Inspect the `students` table schema**:
  ```sql
  \d students
  ```
* **Inspect the `health_records` table schema**:
  ```sql
  \d health_records
  ```
* **Query students**:
  ```sql
  SELECT * FROM students;
  ```
* **Query health records**:
  ```sql
  SELECT * FROM health_records;
  ```
* **Exit psql**:
  ```sql
  \q
  ```

---

## 11. Student ID Behavior

* `Student.student_id` is an **auto-incrementing `BigAutoField` integer primary key**.
* When creating a student, **DO NOT include `student_id`** in the payload. The database generates it sequentially (`1, 2, 3, ...`).
* When creating a health record, supply the generated integer `student_id` of the related student.
* `HealthRecord.health_id` is also auto-incremented by the database.

---

## 12. Run Automated Tests

Run the backend test suite to verify models, serializers, endpoints, and database constraints:

```powershell
python manage.py test clinic
```

### Expected Result:
```text
Ran 31 tests in 0.687s

OK
Destroying test database for alias 'default'...
System check identified no issues (0 silenced).
```

---

## 13. Create Django Admin Superuser (Optional)

Create an administrative account to access the Django Admin interface at `/admin/`:

```powershell
python manage.py createsuperuser
```
Enter your desired username, email address, and password when prompted.

---

## 14. Start the Backend Server

Start the Django local development server on port 8000:

```powershell
python manage.py runserver 8000
```

### Available Endpoints:
* **API Root Discovery**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Students API**: [http://127.0.0.1:8000/api/students/](http://127.0.0.1:8000/api/students/)
* **Health Records API**: [http://127.0.0.1:8000/api/health-records/](http://127.0.0.1:8000/api/health-records/)
* **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 15. Frontend Setup

Open a separate terminal window and navigate to the `frontend` folder:

```powershell
cd frontend
```

### Install Frontend Dependencies
```powershell
npm install
```

### Start Vite Development Server
```powershell
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## 16. Verification Checklist

Use this checklist to confirm your environment is fully operational:

* [ ] Docker Desktop is running.
* [ ] Container `clinic-postgres` is active (`docker ps`).
* [ ] `clinic_db` is reachable on port `5432`.
* [ ] `backend/.env` is configured.
* [ ] Python virtual environment is activated (`(venv)` shown in prompt).
* [ ] Python packages installed (`pip install -r requirements.txt`).
* [ ] Migrations applied successfully (`python manage.py migrate`).
* [ ] Database tables `students` and `health_records` exist.
* [ ] All 31 automated tests pass (`python manage.py test clinic`).
* [ ] Backend server runs on [http://127.0.0.1:8000](http://127.0.0.1:8000).
* [ ] API root responds at `http://127.0.0.1:8000/`.
* [ ] Frontend runs on [http://localhost:5173](http://localhost:5173).

---

## 17. Troubleshooting

### Problem: "The container name '/clinic-postgres' is already in use"
**Solution**: The container was already created previously. Start it instead of running `docker run`:
```powershell
docker start clinic-postgres
```

### Problem: "Error: Port 5432 is already allocated"
**Solution**: A local PostgreSQL service or another container is using port 5432.
* Check running containers: `docker ps`
* Stop conflicting container: `docker stop <container_id>`
* Or stop local Windows PostgreSQL service: `Stop-Service postgresql*`

### Problem: "Error: Port 8000 is already in use"
**Solution**: Start Django on an alternate port:
```powershell
python manage.py runserver 8080
```

### Problem: Checking Migration Status
To inspect which migrations have been applied or are pending:
```powershell
python manage.py showmigrations
```

To verify no uncommitted model changes exist:
```powershell
python manage.py makemigrations --check
```
