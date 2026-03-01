"""Pytest configuration and fixtures for common module tests.

Provides async database engine and session fixtures backed by in-memory
SQLite, reusable across all common test modules.
"""

import pytest

from common.tests.fixtures import (
    create_test_engine,
    create_test_session_factory,
    setup_tables,
)


@pytest.fixture
async def async_engine():
    """Create an in-memory SQLite engine with all tables for the test session.

    Yields:
        AsyncEngine: An engine with all ORM tables created.
    """
    engine = create_test_engine()
    async with engine.begin() as conn:
        await setup_tables(conn)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """Provide an async session that rolls back after each test.

    Ensures every test starts with a clean database state.

    Args:
        async_engine: The test engine fixture.

    Yields:
        AsyncSession: A transactional async session.
    """
    factory = create_test_session_factory(async_engine)
    async with factory() as session:
        yield session
        await session.rollback()
