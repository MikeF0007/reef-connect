"""Unit tests for UserService."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from api_service.app.schemas.user_schemas import (
    PrivacySettingsCreate,
    PrivacySettingsUpdate,
    UserProfileCreate,
    UserProfileUpdate,
    UserSettingsCreate,
    UserSettingsUpdate
)
from api_service.app.services.user_service import UserService
from common.types.enums import UnitSystem, Visibility


class TestUserService:
    """Test cases for UserService methods."""

    @pytest.fixture
    def service(self, mocker):
        """Create a UserService with mocked repository."""
        mock_repo = mocker.Mock()
        return UserService(mock_repo)

    @pytest.fixture
    def user_id(self):
        """Test user ID."""
        return uuid4()

    @pytest.fixture
    def mock_profile(self, user_id):
        """Mock user profile ORM object."""
        from datetime import datetime

        mock = type("MockProfile", (), {})()
        mock.id = user_id
        mock.user_id = user_id
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        mock.first_name = "Michael"
        mock.last_name = "Feldman"
        mock.bio = "Test bio"
        mock.avatar_url = None
        mock.avatar_storage_key = None
        mock.location = None
        mock.website_url = None
        mock.birth_date = None
        return mock

    @pytest.fixture
    def mock_settings(self, user_id):
        """Mock user settings ORM object."""
        from datetime import datetime

        mock = type("MockSettings", (), {})()
        mock.id = user_id
        mock.user_id = user_id
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        mock.preferred_units = UnitSystem.IMPERIAL
        mock.timezone = "UTC"
        mock.language = "en"
        mock.notifications_enabled = True
        return mock

    @pytest.fixture
    def mock_privacy(self, user_id):
        """Mock privacy settings ORM object."""
        from datetime import datetime

        mock = type("MockPrivacy", (), {})()
        mock.id = user_id
        mock.user_id = user_id
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        mock.profile_visibility = Visibility.PUBLIC
        mock.dive_logs_visibility = Visibility.PUBLIC
        mock.media_visibility = Visibility.PUBLIC
        mock.stats_visibility = Visibility.PUBLIC
        return mock

    async def test_create_user_profile(self, service, user_id, mock_profile, mocker):
        """Test creating a user profile."""
        data = UserProfileCreate(first_name="Michael", last_name="Feldman", bio="Test bio")
        service.repository.create_user_profile = AsyncMock(return_value=mock_profile)

        result = await service.create_user_profile(user_id, data)

        service.repository.create_user_profile.assert_called_once_with(
            user_id=user_id,
            profile_data={
                "bio": "Test bio",
                "avatar_url": None,
                "first_name": "Michael",
                "last_name": "Feldman",
                "location": None,
                "website_url": None,
                "birth_date": None,
            },
        )
        assert result.first_name == "Michael"
        assert result.last_name == "Feldman"

    async def test_get_user_profile(self, service, user_id, mock_profile, mocker):
        """Test getting a user profile successfully."""
        service.repository.get_user_profile = AsyncMock(return_value=mock_profile)

        result = await service.get_user_profile(user_id)

        service.repository.get_user_profile.assert_called_once_with(user_id)
        assert result.first_name == "Michael"

    async def test_get_user_profile_not_found(self, service, user_id, mocker):
        """Test getting a user profile that doesn't exist."""
        service.repository.get_user_profile = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="User profile not found"):
            await service.get_user_profile(user_id)

    async def test_update_user_profile(self, service, user_id, mock_profile, mocker):
        """Test updating a user profile."""
        data = UserProfileUpdate(bio="Updated bio")
        service.repository.update_user_profile = AsyncMock(return_value=mock_profile)
        service.repository.get_user_profile = AsyncMock(return_value=mock_profile)

        result = await service.update_user_profile(user_id, data)

        service.repository.update_user_profile.assert_called_once_with(
            user_id, {"bio": "Updated bio"}
        )
        assert result.bio == "Test bio"  # from mock

    async def test_create_user_settings(self, service, user_id, mock_settings, mocker):
        """Test creating user settings."""
        data = UserSettingsCreate(preferred_units=UnitSystem.METRIC, timezone="EST", language="fr")
        service.repository.create_user_settings = AsyncMock(return_value=mock_settings)

        result = await service.create_user_settings(user_id, data)

        service.repository.create_user_settings.assert_called_once_with(
            user_id=user_id,
            settings_data={
                "preferred_units": UnitSystem.METRIC,
                "timezone": "EST",
                "language": "fr",
                "notifications_enabled": True,
            },
        )
        assert result.preferred_units == UnitSystem.IMPERIAL  # from mock

    async def test_get_user_settings(self, service, user_id, mock_settings, mocker):
        """Test getting user settings successfully."""
        service.repository.get_user_settings = AsyncMock(return_value=mock_settings)

        result = await service.get_user_settings(user_id)

        service.repository.get_user_settings.assert_called_once_with(user_id)
        assert result.notifications_enabled is True

    async def test_get_user_settings_not_found(self, service, user_id, mocker):
        """Test getting user settings that don't exist."""
        service.repository.get_user_settings = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="User settings not found"):
            await service.get_user_settings(user_id)

    async def test_update_user_settings(self, service, user_id, mock_settings, mocker):
        """Test updating user settings."""
        data = UserSettingsUpdate(language="fr")
        service.repository.update_user_settings = AsyncMock()
        service.repository.get_user_settings = AsyncMock(return_value=mock_settings)

        result = await service.update_user_settings(user_id, data)

        service.repository.update_user_settings.assert_called_once_with(user_id, {"language": "fr"})
        # The result comes from get_user_settings which returns mock_settings
        assert result.preferred_units == UnitSystem.IMPERIAL

    async def test_create_privacy_settings(self, service, user_id, mock_privacy, mocker):
        """Test creating privacy settings."""
        data = PrivacySettingsCreate(profile_visibility=Visibility.PUBLIC)
        service.repository.create_user_privacy_settings = AsyncMock(return_value=mock_privacy)

        result = await service.create_privacy_settings(user_id, data)

        service.repository.create_user_privacy_settings.assert_called_once_with(
            user_id=user_id,
            privacy_data={
                "profile_visibility": Visibility.PUBLIC,
                "dive_logs_visibility": Visibility.PUBLIC,
                "media_visibility": Visibility.PUBLIC,
                "stats_visibility": Visibility.PUBLIC,
            },
        )
        assert result.profile_visibility == Visibility.PUBLIC

    async def test_get_privacy_settings(self, service, user_id, mock_privacy, mocker):
        """Test getting privacy settings successfully."""
        service.repository.get_user_privacy_settings = AsyncMock(return_value=mock_privacy)

        result = await service.get_privacy_settings(user_id)

        service.repository.get_user_privacy_settings.assert_called_once_with(user_id)
        assert result.profile_visibility == Visibility.PUBLIC

    async def test_get_privacy_settings_not_found(self, service, user_id, mocker):
        """Test getting privacy settings that don't exist."""
        service.repository.get_user_privacy_settings = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Privacy settings not found"):
            await service.get_privacy_settings(user_id)

    async def test_update_privacy_settings(self, service, user_id, mock_privacy, mocker):
        """Test updating privacy settings."""
        data = PrivacySettingsUpdate(profile_visibility=Visibility.PRIVATE)
        service.repository.update_user_privacy_settings = AsyncMock(return_value=mock_privacy)
        service.repository.get_user_privacy_settings = AsyncMock(return_value=mock_privacy)

        result = await service.update_privacy_settings(user_id, data)

        service.repository.update_user_privacy_settings.assert_called_once_with(
            user_id, {"profile_visibility": Visibility.PRIVATE}
        )
        assert result.profile_visibility == Visibility.PUBLIC  # from mock
