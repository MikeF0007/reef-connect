"""Interface for the repository for user-related entities."""

import uuid
from typing import Optional, Protocol

from common.db.models.user_models import PrivacySettings, User, UserProfile, UserSettings


class IUserRepository(Protocol):
    """Protocol defining the contract for user-related CRUD operations."""

    # ================ User CRUD ================

    async def create_user(self, *, email: str, username: str, password_hash: str) -> uuid.UUID:
        """Create a new user and return its ID.

        Args:
            email: The user's email address.
            username: The user's unique username.
            password_hash: Pre-hashed password string.

        Raises:
            sqlalchemy.exc.IntegrityError: If *email* or *username*
                already exists (unique constraint violation).
        """
        ...

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a single user by primary key.

        Args:
            user_id: The user UUID.
        """
        ...

    async def get_users_by_ids(self, user_ids: list[uuid.UUID]) -> list[User]:
        """Fetch multiple users by their IDs in a single query.

        Args:
            user_ids: List of user UUIDs to look up.
        """
        ...

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email address.

        Args:
            email: The email address to search for.
        """
        ...

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by username.

        Args:
            username: The username to search for.
        """
        ...

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user by ID.

        Related profile, settings, privacy settings, certifications, dive logs,
        media (and their species tags), and scubadex entries are cascade-deleted
        by the database.

        Args:
            user_id: The UUID of the user to delete.
        """
        ...

    async def search_users(
        self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[User]:
        """Search users by username or email.

        Args:
            query: Partial username or email to match.
            limit: Maximum number of results to return.
            offset: Number of results to skip.
        """
        ...

    # ================ UserProfile CRUD ================

    async def create_user_profile(
        self, *, user_id: uuid.UUID, profile_data: Optional[dict] = None
    ) -> uuid.UUID:
        """Create a user profile and return its ID.

        Args:
            user_id: ID of the owning user.
            profile_data: Optional field overrides
                (bio, first_name, last_name, etc.).

        Raises:
            sqlalchemy.exc.IntegrityError: If a profile already exists
                for this user or *user_id* does not reference an
                existing user.
        """
        ...

    async def get_user_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Fetch a user's profile by their user ID.

        Args:
            user_id: The user UUID.
        """
        ...

    async def get_user_with_profile(
        self, user_id: uuid.UUID
    ) -> Optional[tuple[User, UserProfile, PrivacySettings]]:
        """Fetch a user with their profile and privacy settings.

        Args:
            user_id: The user UUID.
        """
        ...

    async def update_user_profile(self, user_id: uuid.UUID, updates: dict) -> None:
        """Update specific fields of a user's profile.

        Args:
            user_id: The owning user's UUID.
            updates: Field-name → new-value mapping.
        """
        ...

    # ================ UserSettings CRUD ================

    async def create_user_settings(
        self, *, user_id: uuid.UUID, settings_data: Optional[dict] = None
    ) -> uuid.UUID:
        """Create user settings and return its ID.

        Args:
            user_id: ID of the owning user.
            settings_data: Optional overrides
                (preferred_units, timezone, language).

        Raises:
            sqlalchemy.exc.IntegrityError: If settings already exist
                for this user or *user_id* does not reference an
                existing user.
        """
        ...

    async def get_user_settings(self, user_id: uuid.UUID) -> Optional[UserSettings]:
        """Fetch a user's application settings.

        Args:
            user_id: The user UUID.
        """
        ...

    async def update_user_settings(self, user_id: uuid.UUID, settings: dict) -> None:
        """Update specific application settings for a user.

        Args:
            user_id: The owning user's UUID.
            settings: Field-name → new-value mapping.
        """
        ...

    # ================ PrivacySettings CRUD ================

    async def create_user_privacy_settings(
        self, *, user_id: uuid.UUID, privacy_data: Optional[dict] = None
    ) -> uuid.UUID:
        """Create privacy settings and return its ID.

        Args:
            user_id: ID of the owning user.
            privacy_data: Optional visibility overrides
                (profile_visibility, dive_logs_visibility, etc.).

        Raises:
            sqlalchemy.exc.IntegrityError: If privacy settings already
                exist for this user or *user_id* does not reference an
                existing user.
        """
        ...

    async def get_user_privacy_settings(self, user_id: uuid.UUID) -> Optional[PrivacySettings]:
        """Fetch a user's privacy settings.

        Args:
            user_id: The user UUID.
        """
        ...

    async def update_user_privacy_settings(self, user_id: uuid.UUID, settings: dict) -> None:
        """Update specific privacy settings for a user.

        Args:
            user_id: The owning user's UUID.
            settings: Field-name → new-value mapping.
        """
        ...
