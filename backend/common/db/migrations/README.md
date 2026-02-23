# Database Migrations

This directory contains Alembic database migration scripts for the ReefConnect backend.

## Migration Commands

### Environment Setup

Migrations use the backend's configuration system, which supports different deployment modes:
- **Monolith Mode** (`DEPLOYMENT_MODE=monolith`): Loads from `backend/.env` (ideal for dev/demos).
- **Microservices Mode** (`DEPLOYMENT_MODE=microservices`): Loads from `backend/.env`.

Set the mode when running commands, or add it to your `.env` file.

### During Development

```bash
# Generate migration from model changes (specify mode)
DEPLOYMENT_MODE=monolith alembic revision --autogenerate -m "description of changes"

# Apply migrations to database (specify mode)
DEPLOYMENT_MODE=monolith alembic upgrade head

# Check current migration status
DEPLOYMENT_MODE=monolith alembic current

# View migration history
alembic history  # (No mode needed for read-only commands)
```

### When to Run Migrations

- **After creating new models** - Generate and apply migration
- **After modifying existing models** - Generate and apply migration
- **Before deploying** - Ensure all migrations are applied in the target deployment mode
- **When pulling changes** - Run `DEPLOYMENT_MODE=<mode> alembic upgrade head` to sync database

Note: Model files referred to are files in the common/db/models

### Best Practices

- Always test migrations on a copy of production data first
- Use descriptive commit messages for migration revisions
- Never modify existing migration files manually
- Run migrations in a transaction-safe environment
- Ensure DEPLOYMENT_MODE matches your deployment (monolith for combined setups, microservices for
independent services)

## Directory Structure

- `env.py` - Migration environment configuration
- `script.py.mako` - Migration script template
- `versions/` - Generated migration files (one per revision)
