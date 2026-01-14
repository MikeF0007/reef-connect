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
├── app/
│   ├── api/          # API routes and endpoints
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── core/         # Config, security, database
├── tests/            # Test suite
├── alembic/          # Database migrations
└── requirements.txt  # Python dependencies
```

## API Documentation

Once running, API docs will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
