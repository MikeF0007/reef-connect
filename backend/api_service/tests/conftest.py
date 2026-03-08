"""Pytest configuration and fixtures for api_service tests.

Provides async database session, FastAPI TestClient, and authentication mocking
fixtures for testing the API layer.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api_service.app.app import app
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


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for testing API endpoints.

    Yields:
        TestClient: A client configured with the FastAPI app.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_current_user_id():
    """Mock the current user ID for authentication in tests.

    Returns:
        UUID: A consistent test user ID.
    """
    return uuid4()


@pytest.fixture(autouse=True)
def override_dependencies(mock_current_user_id, async_session):
    """Automatically override authentication and database dependencies in all tests.

    This mocks get_current_user_id to return a consistent test user ID,
    and get_db_session to return the test session.

    Args:
        mock_current_user_id: The test user ID fixture.
        async_session: The test database session fixture.
    """
    from api_service.app.api import certification_api, dive_log_api, user_api
    from common.db.database import get_db_session

    def mock_get_current_user_id():
        return mock_current_user_id

    async def mock_get_db_session():
        return async_session

    # Override the dependencies in both routers
    app.dependency_overrides[user_api.get_current_user_id] = mock_get_current_user_id
    app.dependency_overrides[certification_api.get_current_user_id] = (
        mock_get_current_user_id
    )
    app.dependency_overrides[dive_log_api.get_current_user_id] = (
        mock_get_current_user_id
    )
    app.dependency_overrides[get_db_session] = mock_get_db_session

    yield

    # Clean up overrides after test
    app.dependency_overrides.clear()
