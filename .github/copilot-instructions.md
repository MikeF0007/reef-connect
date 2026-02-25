# ReefConnect AI Coding Agent Instructions

## Project Overview

ReefConnect is a social media platform for scuba divers with microservices backend (Python/FastAPI, async SQLAlchemy, Kafka workers) and React+TypeScript frontend using shadcn/ui. This is a learning project focused on scalable, production-ready full-stack application design and senior-level engineering practices.

## Architecture

- **API Service**: FastAPI REST endpoints
- **Workers**: Event consumers for media/ML/data processing
- **Event Bus**: Kafka/Redpanda messaging
- **Database**: PostgreSQL with SQLAlchemy ORM, Alembic migrations
- **Storage**: S3/MinIO blob storage

## Key Patterns & Conventions

- **Async DB**: Use `AsyncSessionLocal()` for all operations; sync for Alembic
- **Events**: Inherit `Event` class with `event_id`, `timestamp`, `to_dict()`; routing keys like "media_uploaded"
- **Workers**: Extend `EventBasedContainerController`; publish via `KafkaConnectionManager.send_async()`
- **Config**: Pydantic settings; monolith loads `backend/.env` + `.env.monolith`; microservices adds component `.env`
- **Code Quality**: 100 char lines; ruff rules (E,F,I,B,C4,W,D,S,PL,ANN); known-first-party imports ["reef_connect", "backend"]

## Development Workflows

```bash
# Test & lint
nox              # All checks
nox -s test      # Tests only
nox -s fix       # Auto-fix lint

# Setup
cd backend; pip install -r requirements.txt -r api_service/requirements.txt
pip install pre-commit; pre-commit install
```

**Note:** Always use a virtual environment (e.g., venv) for Python development to isolate dependencies. Create one with `python -m venv .venv` if it doesn't exist.

## Common Patterns

**FastAPI Endpoint:**

```python
@app.post("/api/dive-logs")
async def create_dive_log(data: DiveLogCreate, session: AsyncSession = Depends(get_db_session)):
    # Async DB ops
```

**Event Publishing:**

```python
event = MediaUploadedEvent(media_id=media.id, user_id=user.id)
await kafka_manager.send_async("media_events", event.to_dict())
```

**DB Query:**

```python
async with AsyncSessionLocal() as session:
    stmt = select(DiveLog).where(DiveLog.user_id == user_id)
    result = await session.execute(stmt)
    dive_logs = result.scalars().all()
```

## Key Files

- `backend/common/config.py`: Pydantic settings
- `backend/common/db/database.py`: SQLAlchemy setup
- `designs/`: Design docs, PlantUML, API specs
- `frontend/src/`: React components
- `backend/api_service/app/`: FastAPI structure</content>
  <parameter name="filePath">.github/copilot-instructions.md
