"""Shared test fixtures for the ReefConnect backend.

This module provides reusable async database fixtures (engine, session factory,
session) that any test suite can import and wrap as pytest fixtures in its own
conftest.py.

Usage in a component's conftest.py::

    import pytest
    from common.tests.fixtures import (
        create_test_engine,
        create_test_session_factory,
        setup_tables,
    )

    @pytest.fixture
    async def async_engine():
        engine = create_test_engine()
        async with engine.begin() as conn:
            await setup_tables(conn)
        yield engine
        await engine.dispose()

    @pytest.fixture
    async def async_session(async_engine):
        factory = create_test_session_factory(async_engine)
        async with factory() as session:
            yield session
            await session.rollback()
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from common.db.models.base_model import Base

# Import all model modules so Base.metadata is fully populated
import common.db.models.user_models  # noqa: F401
import common.db.models.core_models  # noqa: F401


def create_test_engine() -> AsyncEngine:
    """Create an in-memory SQLite async engine for testing.

    Returns:
        AsyncEngine: An async SQLAlchemy engine backed by in-memory SQLite.
    """
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )


def create_test_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine.

    Args:
        engine: The async engine to bind sessions to.

    Returns:
        async_sessionmaker: A factory that produces AsyncSession instances.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def setup_tables(conn) -> None:  # noqa: ANN001
    """Create all tables defined in Base.metadata.

    Call within an ``async with engine.begin() as conn:`` block.

    Args:
        conn: An async connection from engine.begin().
    """
    await conn.run_sync(Base.metadata.create_all)


async def teardown_tables(conn) -> None:  # noqa: ANN001
    """Drop all tables defined in Base.metadata.

    Call within an ``async with engine.begin() as conn:`` block.

    Args:
        conn: An async connection from engine.begin().
    """
    await conn.run_sync(Base.metadata.drop_all)
