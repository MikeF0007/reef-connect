"""Service layer for user profile, settings, and privacy operations."""

from uuid import UUID

from common.db.repositories.user_repository import UserRepository

from ..schemas.user_schemas import (
    PrivacySettingsCreate,
    PrivacySettingsResponse,
    PrivacySettingsUpdate,
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
    UserSettingsCreate,
    UserSettingsResponse,
    UserSettingsUpdate,
)


class UserService:
    """Service for managing user profiles, settings, and privacy."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def create_user_profile(
        self, user_id: UUID, data: UserProfileCreate
    ) -> UserProfileResponse:
        """Create a new user profile."""
        profile = await self.repository.create_user_profile(
            user_id=user_id, profile_data=data.model_dump()
        )
        return UserProfileResponse.model_validate(profile)

    async def get_user_profile(self, user_id: UUID) -> UserProfileResponse:
        """Get user profile by user ID."""
        # TODO: Implement privacy-aware filtering based on PrivacySettings:
        # - Check the requested user's profile visibility settings
        profile = await self.repository.get_user_profile(user_id)
        if not profile:
            raise ValueError("User profile not found")
        return UserProfileResponse.model_validate(profile)

    async def update_user_profile(
        self, user_id: UUID, data: UserProfileUpdate
    ) -> UserProfileResponse:
        """Update user profile."""
        await self.repository.update_user_profile(
            user_id, data.model_dump(exclude_unset=True)
        )
        return await self.get_user_profile(user_id)

    async def create_user_settings(
        self, user_id: UUID, data: UserSettingsCreate
    ) -> UserSettingsResponse:
        """Create user settings."""
        settings = await self.repository.create_user_settings(
            user_id=user_id, settings_data=data.model_dump()
        )
        return UserSettingsResponse.model_validate(settings)

    async def get_user_settings(self, user_id: UUID) -> UserSettingsResponse:
        """Get user settings by user ID."""
        settings = await self.repository.get_user_settings(user_id)
        if not settings:
            raise ValueError("User settings not found")
        return UserSettingsResponse.model_validate(settings)

    async def update_user_settings(
        self, user_id: UUID, data: UserSettingsUpdate
    ) -> UserSettingsResponse:
        """Update user settings."""
        await self.repository.update_user_settings(
            user_id, data.model_dump(exclude_unset=True)
        )
        return await self.get_user_settings(user_id)

    async def create_privacy_settings(
        self, user_id: UUID, data: PrivacySettingsCreate
    ) -> PrivacySettingsResponse:
        """Create privacy settings."""
        privacy = await self.repository.create_user_privacy_settings(
            user_id=user_id, privacy_data=data.model_dump()
        )
        return PrivacySettingsResponse.model_validate(privacy)

    async def get_privacy_settings(self, user_id: UUID) -> PrivacySettingsResponse:
        """Get privacy settings by user ID."""
        privacy = await self.repository.get_user_privacy_settings(user_id)
        if not privacy:
            raise ValueError("Privacy settings not found")
        return PrivacySettingsResponse.model_validate(privacy)

    async def update_privacy_settings(
        self, user_id: UUID, data: PrivacySettingsUpdate
    ) -> PrivacySettingsResponse:
        """Update privacy settings."""
        await self.repository.update_user_privacy_settings(
            user_id, data.model_dump(exclude_unset=True)
        )
        return await self.get_privacy_settings(user_id)
