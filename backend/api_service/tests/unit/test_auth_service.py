"""Unit tests for AuthService."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from api_service.app.services.auth_service import AuthService


class TestAuthService:
    """Unit tests for AuthService methods."""

    @pytest.fixture
    def service(self, mocker):
        """Create an AuthService with a mocked user repository."""
        mock_repo = mocker.Mock()
        return AuthService(mock_repo)

    @pytest.fixture
    def user_id(self):
        """Test user UUID."""
        return uuid4()

    @pytest.fixture
    def mock_user(self, user_id):
        """Mock User ORM object."""
        mock = type("MockUser", (), {})()
        mock.id = user_id
        mock.email = "test@example.com"
        mock.username = "testuser"
        mock.created_at = datetime.now()
        mock.password_hash = "$2b$12$fakehashvalue"
        return mock

    # ============================================================================
    # Registration Tests
    # ============================================================================

    async def test_register_user_success(self, service, user_id):
        """Test successful registration returns the new user UUID."""
        service.user_repository.create_user = AsyncMock(return_value=user_id)

        result = await service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        assert result == user_id
        call_kwargs = service.user_repository.create_user.call_args.kwargs
        assert call_kwargs["email"] == "test@example.com"
        assert call_kwargs["username"] == "testuser"
        assert call_kwargs["password_hash"] != "password123"  # must be hashed

    async def test_register_user_integrity_error_raises_value_error(self, service):
        """Test that an IntegrityError from the repository is raised as ValueError."""
        service.user_repository.create_user = AsyncMock(
            side_effect=IntegrityError("duplicate key", {}, None)
        )

        with pytest.raises(ValueError, match="already registered"):
            await service.register_user(
                email="test@example.com",
                username="testuser",
                password="password123",
            )

    # ============================================================================
    # Authentication Tests
    # ============================================================================

    async def test_authenticate_user_success(self, service, mock_user, user_id, mocker):
        """Test correct credentials return the user UUID."""
        service.user_repository.get_user_by_email = AsyncMock(return_value=mock_user)
        mocker.patch.object(service, "_verify_password", return_value=True)

        result = await service.authenticate_user(
            email="test@example.com", password="password123"
        )

        assert result == user_id
        service.user_repository.get_user_by_email.assert_called_once_with("test@example.com")

    async def test_authenticate_user_wrong_password(self, service, mock_user, mocker):
        """Test wrong password returns None."""
        service.user_repository.get_user_by_email = AsyncMock(return_value=mock_user)
        mocker.patch.object(service, "_verify_password", return_value=False)

        result = await service.authenticate_user(
            email="test@example.com", password="wrongpassword"
        )

        assert result is None

    async def test_authenticate_user_not_found(self, service):
        """Test unknown email returns None."""
        service.user_repository.get_user_by_email = AsyncMock(return_value=None)

        result = await service.authenticate_user(
            email="unknown@example.com", password="password123"
        )

        assert result is None

    # ============================================================================
    # Retrieval Tests
    # ============================================================================

    async def test_get_user_by_id_found(self, service, mock_user, user_id):
        """Test get_user_by_id returns the user when found."""
        service.user_repository.get_user_by_id = AsyncMock(return_value=mock_user)

        result = await service.get_user_by_id(user_id)

        assert result == mock_user
        service.user_repository.get_user_by_id.assert_called_once_with(user_id)

    async def test_get_user_by_id_not_found(self, service, user_id):
        """Test get_user_by_id returns None when the user does not exist."""
        service.user_repository.get_user_by_id = AsyncMock(return_value=None)

        result = await service.get_user_by_id(user_id)

        assert result is None
