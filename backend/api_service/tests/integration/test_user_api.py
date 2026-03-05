"""Integration tests for user API endpoints."""

from uuid import uuid4

import pytest
from common.db.models.user_models import (
    PrivacySettings,
    UserProfile,
    UserSettings
)
from common.types.enums import UnitSystem, Visibility


class TestUserAPI:
    """Integration tests for user-related API endpoints."""

    @pytest.fixture
    async def test_user_profile(self, async_session, mock_current_user_id):
        """Create a test user profile in the database."""
        profile = UserProfile(
            user_id=mock_current_user_id, first_name="Michael", last_name="Feldman", bio="Test bio"
        )
        async_session.add(profile)
        await async_session.commit()
        await async_session.refresh(profile)
        return profile

    @pytest.fixture
    async def test_user_settings(self, async_session, mock_current_user_id):
        """Create test user settings in the database."""
        settings = UserSettings(
            user_id=mock_current_user_id,
            preferred_units=UnitSystem.IMPERIAL,
            timezone="UTC",
            language="en",
        )
        async_session.add(settings)
        await async_session.commit()
        await async_session.refresh(settings)
        return settings

    @pytest.fixture
    async def test_privacy_settings(self, async_session, mock_current_user_id):
        """Create test privacy settings in the database."""
        privacy = PrivacySettings(
            user_id=mock_current_user_id, profile_visibility=Visibility.PUBLIC
        )
        async_session.add(privacy)
        await async_session.commit()
        await async_session.refresh(privacy)
        return privacy

    async def test_get_my_profile(self, client, test_user_profile):
        """Test GET /users/me/profile."""
        response = client.get("/users/me/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Michael"
        assert data["last_name"] == "Feldman"
        assert data["bio"] == "Test bio"

    async def test_get_my_profile_not_found(self, client):
        """Test GET /users/me/profile when profile doesn't exist."""
        response = client.get("/users/me/profile")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_my_profile(self, client, test_user_profile):
        """Test PATCH /users/me/profile."""
        update_data = {"bio": "Updated bio", "first_name": "Jane"}
        response = client.patch("/users/me/profile", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["bio"] == "Updated bio"

    async def test_update_my_profile_partial(self, client, test_user_profile):
        """Test PATCH /users/me/profile with partial update."""
        update_data = {"bio": "Only bio updated"}
        response = client.patch("/users/me/profile", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Michael"  # unchanged
        assert data["bio"] == "Only bio updated"

    async def test_update_my_profile_invalid_data(self, client, test_user_profile):
        """Test PATCH /users/me/profile with invalid data."""
        invalid_data = {"first_name": ""}  # Empty name
        response = client.patch("/users/me/profile", json=invalid_data)

        assert response.status_code == 422  # Validation error

    async def test_get_my_settings(self, client, test_user_settings):
        """Test GET /users/me/settings."""
        response = client.get("/users/me/settings")

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_units"] == "imperial"
        assert data["timezone"] == "UTC"

    async def test_get_my_settings_not_found(self, client):
        """Test GET /users/me/settings when settings don't exist."""
        response = client.get("/users/me/settings")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_my_settings(self, client, test_user_settings):
        """Test PATCH /users/me/settings."""
        update_data = {"preferred_units": "metric", "language": "fr"}
        response = client.patch("/users/me/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_units"] == "metric"
        assert data["language"] == "fr"

    async def test_get_my_privacy_settings(self, client, test_privacy_settings):
        """Test GET /users/me/privacy."""
        response = client.get("/users/me/privacy")

        assert response.status_code == 200
        data = response.json()
        assert data["profile_visibility"] == "public"

    async def test_get_my_privacy_settings_not_found(self, client):
        """Test GET /users/me/privacy when settings don't exist."""
        response = client.get("/users/me/privacy")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_my_privacy_settings(self, client, test_privacy_settings):
        """Test PATCH /users/me/privacy."""
        update_data = {"profile_visibility": "private"}
        response = client.patch("/users/me/privacy", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["profile_visibility"] == "private"

    async def test_get_user_profile(self, client, async_session):
        """Test GET /users/{user_id}/profile for another user."""
        other_user_id = uuid4()
        profile = UserProfile(
            user_id=other_user_id, first_name="Other", last_name="User", bio="Other bio"
        )
        async_session.add(profile)
        await async_session.commit()

        response = client.get(f"/users/{other_user_id}/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Other"
        assert data["last_name"] == "User"

    async def test_get_user_profile_not_found(self, client):
        """Test GET /users/{user_id}/profile for nonexistent user."""
        random_id = uuid4()
        response = client.get(f"/users/{random_id}/profile")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
