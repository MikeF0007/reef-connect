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

## API Documentation

Once running, API docs will be available at:
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

## Coming Soon
- Virtual environment setup
- Database configuration
- Running migrations
- Running tests
