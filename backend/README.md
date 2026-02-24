# ReefConnect Backend

Microservices-based backend for the ReefConnect social dive logging platform, featuring a FastAPI
REST API and async workers for data processing.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM for database interactions
- **Alembic** - Database migrations
- **Pydantic** - Data validation and settings management

## Development Setup

- **Install dependencies**
  `pip install -r api_service/requirements.txt`
- **Run the API server**:
  `python -m uvicorn backend.api_service.app.app:app --reload` (from project root)

## Environment Configuration

The backend supports two deployment modes to balance scalability with development convenience. This
approach allows the system to scale microservices independently while maintaining monolith
convenience for early development and small-scale demos.

### Deployment Modes

**Monolith Mode**
- Loads from `backend/.env` (shared backend config) and, if present, `backend/.env.monolith`
(monolith-specific overrides). Use `.env.monolith` for variables unique to monolith mode or
overriding `backend/.env`. This include service-level configs since monolith mode does not load
service configs.
- (`DEPLOYMENT_MODE=monolith`)
**Microservices Mode**
- Assuming this is related to one service deployment, loads from `backend/.env` (shared backend
config) and, if present, the given service's `.env` (e.g., `api_service/.env`) for overrides or
service specific configuration.
- (`DEPLOYMENT_MODE=microservices`)

TODO: Consider adopting ENV_FILE selector approach for simplifying handling of dev/stage/prod vars
as the project grows. For now, the current setup is sufficient for early development/deployment.

### Setup

1. Copy the base `backend/.env.example` to `backend/.env` (shared backend config).
2. Copy the appropriate mode-specific `.env.example` files:
   - For monolith mode: Copy `backend/.env.monolith.example` to `backend/.env.monolith`
   - For microservices mode: For given component (e.g., `api_service/`), copy its `.env.example` to
   `component/.env`
3. Adjust variables as needed (e.g., database URLs, secrets).
4. Set `DEPLOYMENT_MODE` in your environment or `.env` file.

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

Planned structure:

```
backend/
├── api_service/                # API service for external clients (i.e. frontend)
│   ├── app/                      # App structured for FastAPI
│   │   ├── api/                    # API routes and endpoints
│   │   ├── schemas/                # Pydantic schemas (API-specific)
│   │   ├── services/               # Business logic
│   │   └── core/                   # Config, security, database connections
│   ├── tests/                      # Test suite
│   └── requirements.txt            # Python dependencies
├── common/                     # Common classes, enums, utilities, config, and shared DB components
│   ├── container/                # Container management and dependency injection
│   ├── db/                       # Database-related components
│   │   ├── models/                 # ORM models (using SQLAlchemy)
│   │   ├── migrations/             # Database migrations (using Alembic)
│   │   └── repositories/           # Data access repositories
│   ├── types/                    # Common types, enums, and event types
│   └── utils/                    # General utility functions and helpers
├── materialized_data_worker/   # Async worker to produce materialized data (i.e. ScubaDex)
│   ├── app/                      # Main worker code
│   └── tests/                    # Test suite
├── media_worker/               # Async worker to process media uploaded by users
│   ├── app/                      # Main worker code
│   └── tests/                    # Worker tests
└── ml_tagger_worker/           # Async worker to use ML model to tag fish species in user media
    ├── app/                      # Main worker code
    └── tests/                    # Worker tests
```

## Virtual Environment Setup

It is recommended to use a Python virtual environment for development:

```bash
# Create a virtual environment (if not already created)
python -m venv .venv

# Activate the virtual environment:
# Windows, Command Prompt
.venv\Scripts\activate
# Windows, PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r api_service/requirements.txt
```

## Database Migrations

For migration commands and environment setup, see [common/db/migrations/README.md](common/db/migrations/README.md).

## Coming Soon
- Database configuration
- Running tests
