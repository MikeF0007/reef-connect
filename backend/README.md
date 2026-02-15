# ReefConnect Backend

FastAPI-based REST API for the ReefConnect social dive logging platform.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM for database interactions
- **Alembic** - Database migrations
- **Pydantic** - Data validation and settings management

## Development Setup

Coming soon - will include:
- Virtual environment setup
- Database configuration
- Running migrations
- API development server
- Running tests

## Project Structure

Planned structure:
```
backend/
├── api_service/                # API service for external clients (i.e. frontend)
│   ├── app/                      # App structured for FastAPI
│   │   ├── api/                    # API routes and endpoints
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   └── core/                   # Config, security, database
│   ├── tests/                      # Test suite
│   ├── alembic/                    # Database migrations
│   └── requirements.txt            # Python dependencies
├── common/                     # Common classes, enums, utilities, config, etc.
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

## API Documentation

Once running, API docs will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
