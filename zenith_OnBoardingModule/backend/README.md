# Zenith — Backend

Production-grade FastAPI backend boilerplate for an AI-based Project Evaluation Platform.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 15 + SQLAlchemy 2.0 (async) + MongoDB 7 (Motor) |
| Migrations | Alembic (PostgreSQL) |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Task Queue | Celery + Redis |
| Container | Docker Compose |
| Testing | pytest + pytest-asyncio + httpx |
| Logging | structlog |

---

## Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/          # health.py · auth.py · users.py
│   │       └── router.py        # aggregates all v1 routes
│   ├── auth/
│   │   ├── dependencies.py      # FastAPI Depends helpers & RBAC guards
│   │   └── handlers.py          # token generation / refresh utilities
│   ├── core/
│   │   ├── config.py            # Pydantic Settings (env-based)
│   │   ├── database.py          # async engine, session, Base
│   │   ├── exceptions.py        # typed app exceptions + handlers
│   │   ├── logging.py           # structlog configuration
│   │   └── security.py          # JWT encode/decode, password hashing
│   ├── models/
│   │   ├── base.py              # UUIDPrimaryKeyMixin · TimestampMixin · SoftDeleteMixin
│   │   └── user.py              # User SQLAlchemy model + UserRole enum
│   ├── repositories/
│   │   ├── base.py              # Generic BaseRepository[ModelType]
│   │   └── user_repository.py   # UserRepository extends BaseRepository
│   ├── schemas/
│   │   ├── base.py              # BaseSchema · PaginatedResponse · MessageResponse
│   │   ├── auth.py              # LoginRequest · TokenResponse · RefreshTokenRequest
│   │   └── user.py              # UserCreate · UserUpdate · UserResponse
│   ├── services/
│   │   ├── base.py              # Generic BaseService[ModelType, RepositoryType]
│   │   └── user_service.py      # UserService extends BaseService
│   ├── tasks/
│   │   └── example_tasks.py     # Celery task stubs
│   ├── utils/
│   │   ├── helpers.py           # random strings, UTC time, dict sanitizer
│   │   └── pagination.py        # paginate() helper + PaginatedResult
│   ├── workers/
│   │   └── celery_app.py        # Celery application factory
│   └── main.py                  # FastAPI app factory + middleware + exception handlers
├── alembic/
│   ├── versions/                # auto-generated migration files
│   ├── env.py                   # async Alembic env wired to app settings
│   └── script.py.mako           # migration template
├── tests/
│   ├── conftest.py              # in-memory SQLite fixtures + async test client
│   ├── test_auth.py             # auth endpoint tests
│   └── test_users.py            # user CRUD tests
├── docker/
│   ├── Dockerfile               # multi-stage API image
│   └── Dockerfile.worker        # multi-stage Celery worker image
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env.example
├── alembic.ini
└── docker-compose.yml
```

---

## Local Development Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15
- MongoDB 7
- Redis 7
- Docker & Docker Compose (optional)

### 2. Clone & create virtual environment

```bash
git clone <repo-url>
cd backend
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY, etc.
```

Generate a secure `SECRET_KEY`:

```bash
openssl rand -hex 32
```

### Import the BLK onboarding tracker

The onboarding dashboard reads employee and milestone records from MongoDB. Preview
the workbook import (dry-run; no database writes) with:

```bash
python scripts/import_blk_onboarding.py
```

Apply it to the MongoDB configured in `.env` with:

```bash
python scripts/import_blk_onboarding.py --apply
```

The default workbook is `../onboarding_dashboard/data/BLK Onboarding Tracker.xlsx`.
Employee identities come from the names in row 2 of `Phase1 - Machine Setup`.
The Resource List's `VLinker` values are role labels, not employee names, so they
are not used as identities or as a source for client/project assignments. Blank
employee IDs and unlinked roster fields stay blank. The import creates pending
onboarding records and seeds Week0/Day0–Day5 activity templates without replacing
existing progress; it does not create user accounts or passwords. On re-import, it
archives legacy records whose only identity was a Resource List role label.

### 5. Create the databases

```bash
# PostgreSQL
psql -U postgres -c "CREATE DATABASE zenith;"

# MongoDB (optional - MongoDB creates databases automatically on first use)
# The database will be created when you first write to it
```

### 6. Run migrations

```bash
# Generate the initial migration (first time only)
alembic revision --autogenerate -m "initial"

# Apply all pending migrations
alembic upgrade head
```

### 7. Start the development server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs

---

## Yearly Holiday Lists

Authenticated users can upload a holiday schedule PDF from **Settings → Holiday List**.
The PDF must contain `Holiday Name`, `Day`, `Date`, and `Type` columns; the year is
derived from each date. Imported rows are stored in the `yearly_holiday` collection
inside the `zenith` MongoDB database, replacing existing rows for each imported year.
The Home page displays the current year's holiday names and dates with weekdays below
the Leave Balance card.

API endpoints:

- `POST /api/v1/holidays/import` — upload a PDF as multipart field `file`.
- `GET /api/v1/holidays?year=2026` — retrieve holidays for a year (defaults to the
  current year).

---

## Running with Docker Compose

> **Prerequisite:** `docker.io` does not include the Compose plugin.
> Install it first:
> ```bash
> sudo apt install docker-compose-v2
> sudo usermod -aG docker $USER   # allow running without sudo (re-login after)
> ```

All `docker compose` commands must be run from the `backend/` directory
(where `docker-compose.yml` lives):

```bash
cd backend

# Start the full stack (API + DB + Redis + Worker + Frontend)
docker compose up --build --force-recreate

# Start with optional tools (pgAdmin + MinIO)
docker compose --profile tools up --build --force-recreate

# Run in background
docker compose up -d --build --force-recreate

# After frontend source changes, rebuild and restart only the frontend
docker compose up --build --force-recreate frontend

# View logs
docker compose logs -f api
docker compose logs -f worker

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

---

## Database Migrations

```bash
# Create a new auto-detected migration
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show migration history
alembic history --verbose
```

---

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_auth.py -v

# Run a specific test
pytest tests/test_auth.py::test_login_success -v
```

---

## Celery Workers

```bash
# Start the worker locally
celery -A app.workers.celery_app:celery_app worker --loglevel=info --queues=default

# Monitor tasks (Flower UI)
pip install flower
celery -A app.workers.celery_app:celery_app flower --port=5555
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/health` | — | Health check |
| GET | `/api/v1/health/db` | — | Database connectivity check |
| POST | `/api/v1/auth/login` | — | Obtain JWT token pair |
| POST | `/api/v1/auth/refresh` | — | Refresh access token |
| POST | `/api/v1/auth/logout` | — | Logout (client-side token invalidation) |
| POST | `/api/v1/users` | — | Create user |
| GET | `/api/v1/users/me` | Bearer | Get current user profile |
| GET | `/api/v1/users` | Admin | List all users (paginated) |
| GET | `/api/v1/users/{id}` | Bearer | Get user by ID |
| PATCH | `/api/v1/users/{id}` | Bearer | Update user |
| DELETE | `/api/v1/users/{id}` | Admin | Soft-delete user |

---

## RBAC Roles

| Role | Description |
|---|---|
| `admin` | Full access |
| `moderator` | Elevated access |
| `evaluator` | Evaluator access (AI pipeline use) |
| `user` | Standard access |

Extend roles in `app/models/user.py → UserRole` and guards in `app/auth/dependencies.py`.

---

## Adding a New Module

### For PostgreSQL (Structured Data)

Follow the User module as a reference:

1. **Model** — `app/models/your_entity.py` (extend `Base`, use mixins)
2. **Schema** — `app/schemas/your_entity.py` (extend `BaseSchema`)
3. **Repository** — `app/repositories/your_entity_repository.py` (extend `BaseRepository`)
4. **Service** — `app/services/your_entity_service.py` (extend `BaseService`)
5. **Routes** — `app/api/v1/routes/your_entity.py` (use DI for session + auth)
6. **Register** — Include the router in `app/api/v1/router.py`
7. **Migration** — `alembic revision --autogenerate -m "add your_entity"`

### For MongoDB (Flexible/Rapidly Changing Data)

Use MongoDB for data with evolving schemas, document structures, or high write throughput:

1. **Repository** — `app/repositories/your_entity_repository.py` (extend `MongoBaseRepository`)
2. **Schema** — `app/schemas/your_entity.py` (Pydantic models for validation)
3. **Service** — `app/services/your_entity_service.py` (use MongoDB repository)
4. **Routes** — `app/api/v1/routes/your_entity.py` (use `get_mongodb` dependency)
5. **Register** — Include the router in `app/api/v1/router.py`

Example MongoDB repository:

```python
from app.repositories.mongo_base import MongoBaseRepository

class EvaluationRepository(MongoBaseRepository):
    def __init__(self):
        super().__init__(collection_name="evaluations")

    async def get_by_project_id(self, project_id: str):
        return await self.find_many({"project_id": project_id})
```

Example usage in routes:

```python
from app.core.mongodb import get_mongodb
from app.repositories.mongo_base import MongoBaseRepository

@router.post("/evaluations")
async def create_evaluation(
    data: EvaluationCreate,
    db = Depends(get_mongodb)
):
    repo = MongoBaseRepository("evaluations")
    result = await repo.create(data.model_dump())
    return result
```

---

## Environment Reference

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `local` | `local` / `development` / `staging` / `production` |
| `DATABASE_URL` | — | `postgresql+asyncpg://...` |
| `MONGODB_URL` | `mongodb://mongo:mongo@localhost:27018/zenith?authSource=admin` | Host connection to the MongoDB Compose service; use `mongodb:27017` from inside Compose |
| `MONGODB_DATABASE` | `zenith` | MongoDB database name |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `SECRET_KEY` | auto-generated | JWT signing key — **must be set in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `LOG_FORMAT` | `json` | `json` for prod, `console` for local dev |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Celery result store |
