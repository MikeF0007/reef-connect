"""Module providing SQLAlchemy database connection and session management for backend.

NOTE: This file provides the raw database infrastructure. The API service will create
FastAPI-specific dependency injection wrappers around these engines/sessions for use in endpoint
handlers.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from common.config import settings
from common.db.models.base import Base


# ============================================================================
# Async Engine & Session (for FastAPI endpoints)
# ============================================================================

# Create async engine for database operations
async_engine: AsyncEngine = create_async_engine(
    settings.database_url_str,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Enable connection health checks
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy loading issues after commit
    autoflush=False,
    autocommit=False,
)


# ============================================================================
# Sync Engine & Session (for Alembic migrations)
# ============================================================================

# Create sync engine for Alembic migrations
sync_engine = create_engine(
    settings.database_sync_url_str,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    future=True,
)

# Create sync session factory for migrations/scripts
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
)


# ============================================================================
# Database Lifecycle Functions
# ============================================================================


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLAlchemy models.
    Only use for development/testing. In production, use Alembic migrations.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections.

    Properly dispose of the async engine and all connections.
    Should be called on application shutdown.
    """
    await async_engine.dispose()


def get_sync_db() -> Session:
    """Get synchronous database session for scripts/migrations.

    Returns:
        Session: Synchronous database session
    """
    return SyncSessionLocal()
