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
        """Create a new user profile.

        Args:
            user_id (UUID): The ID of the user to create the profile for.
            data (UserProfileCreate): The profile data to create.

        Returns:
            UserProfileResponse: The newly created user profile.
        """
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
        """Update user profile.

        Args:
            user_id (UUID): The ID of the user to update the profile for.
            data (UserProfileUpdate): The profile fields to update.

        Returns:
            UserProfileResponse: The updated user profile.
        """
        await self.repository.update_user_profile(
            user_id, data.model_dump(exclude_unset=True)
        )
        return await self.get_user_profile(user_id)

    async def create_user_settings(
        self, user_id: UUID, data: UserSettingsCreate
    ) -> UserSettingsResponse:
        """Create user settings.

        Args:
            user_id (UUID): The ID of the user to create the settings for.
            data (UserSettingsCreate): The settings data to create.

        Returns:
            UserSettingsResponse: The newly created user settings.
        """
        settings = await self.repository.create_user_settings(
            user_id=user_id, settings_data=data.model_dump()
        )
        return UserSettingsResponse.model_validate(settings)

    async def get_user_settings(self, user_id: UUID) -> UserSettingsResponse:
        """Get user settings by user ID.

        Args:
            user_id (UUID): The ID of the user whose settings to retrieve.

        Returns:
            UserSettingsResponse: The user settings response.
        """
        settings = await self.repository.get_user_settings(user_id)
        if not settings:
            raise ValueError("User settings not found")
        return UserSettingsResponse.model_validate(settings)

    async def update_user_settings(
        self, user_id: UUID, data: UserSettingsUpdate
    ) -> UserSettingsResponse:
        """Update user settings.

        Args:
            user_id (UUID): The ID of the user to update the settings for.
            data (UserSettingsUpdate): The settings fields to update.

        Returns:
            UserSettingsResponse: The updated user settings.
        """
        await self.repository.update_user_settings(
            user_id, data.model_dump(exclude_unset=True)
        )
        return await self.get_user_settings(user_id)

    async def create_privacy_settings(
        self, user_id: UUID, data: PrivacySettingsCreate
    ) -> PrivacySettingsResponse:
        """Create privacy settings.

        Args:
            user_id (UUID): The ID of the user to create the privacy settings for.
            data (PrivacySettingsCreate): The privacy settings data to create.

        Returns:
            PrivacySettingsResponse: The newly created privacy settings.
        """
        privacy = await self.repository.create_user_privacy_settings(
            user_id=user_id, privacy_data=data.model_dump()
        )
        return PrivacySettingsResponse.model_validate(privacy)

    async def get_privacy_settings(self, user_id: UUID) -> PrivacySettingsResponse:
        """Get privacy settings by user ID.

        Args:
            user_id (UUID): The ID of the user whose privacy settings to retrieve.

        Returns:
            PrivacySettingsResponse: The privacy settings response.
        """
        privacy = await self.repository.get_user_privacy_settings(user_id)
        if not privacy:
            raise ValueError("Privacy settings not found")
        return PrivacySettingsResponse.model_validate(privacy)

    async def update_privacy_settings(
        self, user_id: UUID, data: PrivacySettingsUpdate
    ) -> PrivacySettingsResponse:
        """Update privacy settings.

        Args:
            user_id (UUID): The ID of the user to update the privacy settings for.
            data (PrivacySettingsUpdate): The privacy settings fields to update.

        Returns:
            PrivacySettingsResponse: The updated privacy settings.
        """
        await self.repository.update_user_privacy_settings(
            user_id, data.model_dump(exclude_unset=True)
        )
        return await self.get_privacy_settings(user_id)
