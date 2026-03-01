"""DB-based IUserRepository implementation.

Provides async CRUD operations for user-related entities.
"""

import uuid
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.db.models.user_models import (
    PrivacySettings,
    User,
    UserProfile,
    UserSettings,
)
from common.db.repositories.interfaces import IUserRepository


class UserRepository(IUserRepository):
    """Provides async CRUD operations for User, UserProfile, UserSettings, & PrivacySettings models.

    Attributes:
        session: AsyncSession  -- AsyncSession for database operations. This session is used for
            all method calls, ensuring transaction consistency across operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ================ User CRUD ================

    async def create_user(self, *, email: str, username: str, password_hash: str) -> uuid.UUID:
        """Create a new user and return its ID.

        Args:
            email: User email address.
            username: Unique username.
            password_hash: Pre-hashed password.

        Returns:
            The UUID of the newly created user.

        Raises:
            sqlalchemy.exc.IntegrityError: If *email* or *username*
                already exists (unique constraint violation).
        """
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
        )
        self.session.add(user)
        await self.session.flush()
        return user.id

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a single user by primary key.

        Args:
            user_id: The user UUID.

        Returns:
            The User if found, otherwise ``None``.
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_users_by_ids(self, user_ids: list[uuid.UUID]) -> list[User]:
        """Fetch multiple users by their IDs in a single query.

        Args:
            user_ids: UUIDs to look up.

        Returns:
            A list of found User instances (missing IDs are silently skipped).
        """
        if not user_ids:
            return []
        stmt = select(User).where(User.id.in_(user_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email address.

        Args:
            email: The email to look up.

        Returns:
            The User if found, otherwise ``None``.
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by username.

        Args:
            username: The username to look up.

        Returns:
            The User if found, otherwise ``None``.
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user by ID.

        Related profile, settings, privacy settings, certifications, dive logs,
        media (and their species tags), and scubadex entries are cascade-deleted
        by the database.

        Args:
            user_id: The UUID of the user to delete.

        Returns:
            ``True`` if the user was deleted, ``False`` if not found.
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return False
        await self.session.delete(user)
        await self.session.flush()
        return True

    async def search_users(
        self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[User]:
        """Search users by username or email (case-insensitive partial match).

        Args:
            query: The search string.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            A paginated list of matching users.
        """
        pattern = f"%{query}%"
        stmt = select(User).where(
            or_(
                User.username.ilike(pattern),
                User.email.ilike(pattern),
            ),
        )
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ================ UserProfile CRUD ================

    async def create_user_profile(
        self, *, user_id: uuid.UUID, profile_data: Optional[dict] = None
    ) -> uuid.UUID:
        """Create a user profile and return its ID.

        Args:
            user_id: ID of the owning user.
            profile_data: Optional dict of profile fields
                (bio, first_name, last_name, location, website_url, birth_date).

        Returns:
            The UUID of the newly created profile.

        Raises:
            sqlalchemy.exc.IntegrityError: If a profile already exists
                for this user or *user_id* does not reference an
                existing user.
        """
        data = profile_data or {}
        profile = UserProfile(user_id=user_id, **data)
        self.session.add(profile)
        await self.session.flush()
        return profile.id

    async def get_user_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Fetch a user's profile by their user ID.

        Args:
            user_id: The user UUID.

        Returns:
            The UserProfile if found, otherwise ``None``.
        """
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_with_profile(
        self, user_id: uuid.UUID
    ) -> Optional[tuple[User, UserProfile, PrivacySettings]]:
        """Fetch a user with their profile and privacy settings.

        Uses eager loading for a single efficient query.

        Args:
            user_id: The user UUID.

        Returns:
            A tuple of (User, UserProfile, PrivacySettings) if the user
            exists, otherwise ``None``.  Profile or privacy may be ``None``
            within the tuple if those records don't exist yet.
        """
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.privacy_settings),
            )
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return (user, user.profile, user.privacy_settings)

    async def update_user_profile(self, user_id: uuid.UUID, updates: dict) -> None:
        """Update specific fields of a user's profile.

        Only fields present in *updates* are modified.  Set a value to
        ``None`` to clear a field.

        Args:
            user_id: The owning user's UUID.
            updates: Field-name → new-value mapping.
        """
        profile = await self.get_user_profile(user_id)
        if profile is None:
            return
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        self.session.add(profile)
        await self.session.flush()

    # ================ UserSettings CRUD ================

    async def create_user_settings(
        self, *, user_id: uuid.UUID, settings_data: Optional[dict] = None
    ) -> uuid.UUID:
        """Create user settings (with defaults) and return its ID.

        Args:
            user_id: ID of the owning user.
            settings_data: Optional overrides
                (preferred_units, timezone, language).

        Returns:
            The UUID of the newly created settings row.

        Raises:
            sqlalchemy.exc.IntegrityError: If settings already exist
                for this user or *user_id* does not reference an
                existing user.
        """
        data = settings_data or {}
        user_settings = UserSettings(user_id=user_id, **data)
        self.session.add(user_settings)
        await self.session.flush()
        return user_settings.id

    async def get_user_settings(self, user_id: uuid.UUID) -> Optional[UserSettings]:
        """Fetch a user's application settings.

        Args:
            user_id: The user UUID.

        Returns:
            The UserSettings if found, otherwise ``None``.
        """
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_settings(self, user_id: uuid.UUID, settings: dict) -> None:
        """Update specific application settings for a user.

        Only fields present in *settings* are modified.  Set a value to
        ``None`` to reset to the model default.

        Args:
            user_id: The owning user's UUID.
            settings: Field-name → new-value mapping.
        """
        user_settings = await self.get_user_settings(
            user_id,
        )
        if user_settings is None:
            return
        for key, value in settings.items():
            if hasattr(user_settings, key):
                setattr(user_settings, key, value)
        self.session.add(user_settings)
        await self.session.flush()

    # ================ PrivacySettings CRUD ================

    async def create_user_privacy_settings(
        self, *, user_id: uuid.UUID, privacy_data: Optional[dict] = None
    ) -> uuid.UUID:
        """Create privacy settings (with defaults) and return its ID.

        Args:
            user_id: ID of the owning user.
            privacy_data: Optional visibility overrides
                (profile_visibility, dive_logs_visibility, etc.).

        Returns:
            The UUID of the newly created privacy settings row.

        Raises:
            sqlalchemy.exc.IntegrityError: If privacy settings already
                exist for this user or *user_id* does not reference an
                existing user.
        """
        data = privacy_data or {}
        privacy = PrivacySettings(user_id=user_id, **data)
        self.session.add(privacy)
        await self.session.flush()
        return privacy.id

    async def get_user_privacy_settings(self, user_id: uuid.UUID) -> Optional[PrivacySettings]:
        """Fetch a user's privacy settings.

        Args:
            user_id: The user UUID.

        Returns:
            The PrivacySettings if found, otherwise ``None``.
        """
        stmt = select(PrivacySettings).where(
            PrivacySettings.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_privacy_settings(self, user_id: uuid.UUID, settings: dict) -> None:
        """Update specific privacy settings for a user.

        Only fields present in *settings* are modified.  Set a value to
        ``None`` to reset to the default PUBLIC visibility.

        Args:
            user_id: The owning user's UUID.
            settings: Field-name → new-value mapping.
        """
        privacy = await self.get_user_privacy_settings(
            user_id,
        )
        if privacy is None:
            return
        for key, value in settings.items():
            if hasattr(privacy, key):
                setattr(privacy, key, value)
        self.session.add(privacy)
        await self.session.flush()
