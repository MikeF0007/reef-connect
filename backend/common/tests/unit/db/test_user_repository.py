"""Unit tests for UserRepository.

Tests cover CRUD operations for User, UserProfile, UserSettings, and PrivacySettings against an
in-memory SQLite database.
"""

import uuid
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.repositories.user_repository import UserRepository
from common.types import UnitSystem, Visibility


async def _create_test_user(session: AsyncSession, **overrides: Any) -> uuid.UUID:
    """Insert a user with sensible defaults, returning its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        overrides: Field values to override the defaults (e.g. email, username).

    Returns:
        The UUID of the created user.
    """
    defaults = {
        "email": f"{uuid.uuid4().hex[:8]}@example.com",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password_hash": "hashed_pw",
    }
    defaults.update(overrides)
    return await UserRepository(session).create_user(**defaults)


class TestUserRepository:
    """Tests for UserRepository covering all CRUD operations."""

    # ============================================================================
    # User Creation Tests
    # ============================================================================

    async def test_create_user_returns_uuid(self, async_session: AsyncSession) -> None:
        """Creating a user returns a UUID.

        Args:
            async_session: Database session for the test.
        """
        user_id = await UserRepository(async_session).create_user(
            email="michael@example.com",
            username="michael",
            password_hash="hashed_pw",
        )
        assert isinstance(user_id, uuid.UUID)

    async def test_create_user_persists_fields(self, async_session: AsyncSession) -> None:
        """All required fields are persisted and defaults applied.

        Args:
            async_session: Database session for the test.
        """
        user_id = await UserRepository(async_session).create_user(
            email="michael@example.com",
            username="michael",
            password_hash="hashed_pw",
        )
        user = await UserRepository(async_session).get_user_by_id(user_id)
        assert user is not None
        assert user.email == "michael@example.com"
        assert user.username == "michael"
        assert user.password_hash == "hashed_pw"
        assert user.email_verified is False
        assert user.mfa_enabled is False

    async def test_create_user_duplicate_email(self, async_session: AsyncSession) -> None:
        """Inserting a duplicate email raises an IntegrityError.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_user(async_session, email="dup@example.com")
        with pytest.raises(IntegrityError):
            await _create_test_user(async_session, email="dup@example.com")

    async def test_create_user_duplicate_username(self, async_session: AsyncSession) -> None:
        """Inserting a duplicate username raises an IntegrityError.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_user(async_session, username="taken")
        with pytest.raises(IntegrityError):
            await _create_test_user(async_session, username="taken")

    # ============================================================================
    # User Lookup Tests
    # ============================================================================

    async def test_get_user_by_id(self, async_session: AsyncSession) -> None:
        """Lookup by ID returns the correct user.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        fetched = await UserRepository(async_session).get_user_by_id(user_id)
        assert fetched is not None
        assert fetched.id == user_id

    async def test_get_user_by_id_not_found(self, async_session: AsyncSession) -> None:
        """Lookup by non-existent ID returns None.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_by_id(
            uuid.uuid4(),
        )
        assert result is None

    async def test_get_users_by_ids(self, async_session: AsyncSession) -> None:
        """Batch lookup returns only existing users.

        Args:
            async_session: Database session for the test.
        """
        id1 = await _create_test_user(async_session)
        id2 = await _create_test_user(async_session)
        missing = uuid.uuid4()

        users = await UserRepository(async_session).get_users_by_ids(
            [id1, id2, missing],
        )
        found_ids = {u.id for u in users}
        assert id1 in found_ids
        assert id2 in found_ids
        assert missing not in found_ids

    async def test_get_users_by_ids_empty_list(self, async_session: AsyncSession) -> None:
        """Empty input returns an empty list without hitting the DB.

        Args:
            async_session: Database session for the test.
        """
        users = await UserRepository(async_session).get_users_by_ids([])
        assert users == []

    async def test_get_user_by_email(self, async_session: AsyncSession) -> None:
        """Lookup by email returns the correct user.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(
            async_session, email="lookup@example.com",
        )
        fetched = await UserRepository(async_session).get_user_by_email(
            "lookup@example.com",
        )
        assert fetched is not None
        assert fetched.id == user_id

    async def test_get_user_by_email_not_found(self, async_session: AsyncSession) -> None:
        """Lookup by non-existent email returns None.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_by_email(
            "ghost@example.com",
        )
        assert result is None

    async def test_get_user_by_username(self, async_session: AsyncSession) -> None:
        """Lookup by username returns the correct user.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(
            async_session, username="findme",
        )
        fetched = await UserRepository(async_session).get_user_by_username(
            "findme",
        )
        assert fetched is not None
        assert fetched.id == user_id

    async def test_get_user_by_username_not_found(self, async_session: AsyncSession) -> None:
        """Lookup by non-existent username returns None.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_by_username(
            "nope",
        )
        assert result is None

    # ============================================================================
    # User Deletion Tests
    # ============================================================================

    async def test_delete_user_returns_true(self, async_session: AsyncSession) -> None:
        """Deleting an existing user returns True.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        result = await UserRepository(async_session).delete_user(user_id)
        assert result is True

    async def test_delete_user_removes_from_db(self, async_session: AsyncSession) -> None:
        """After deletion the user is no longer found.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).delete_user(user_id)
        assert await UserRepository(async_session).get_user_by_id(
            user_id,
        ) is None

    async def test_delete_user_not_found(self, async_session: AsyncSession) -> None:
        """Deleting a non-existent user returns False.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).delete_user(
            uuid.uuid4(),
        )
        assert result is False

    # ============================================================================
    # User Search Tests
    # ============================================================================

    async def test_search_by_username(self, async_session: AsyncSession) -> None:
        """Partial username match returns the user.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_user(async_session, username="diver_michael")
        await _create_test_user(async_session, username="diver_bob")
        await _create_test_user(async_session, username="swimmer")

        results = await UserRepository(async_session).search_users(
            "diver",
        )
        usernames = [u.username for u in results]
        assert "diver_michael" in usernames
        assert "diver_bob" in usernames
        assert "swimmer" not in usernames

    async def test_search_by_email(self, async_session: AsyncSession) -> None:
        """Partial email match returns the user.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_user(
            async_session, email="michael@reef.com", username="a1",
        )
        results = await UserRepository(async_session).search_users(
            "reef.com",
        )
        assert len(results) >= 1
        assert results[0].email == "michael@reef.com"

    async def test_search_with_pagination(self, async_session: AsyncSession) -> None:
        """Limit and offset control the result window.

        Args:
            async_session: Database session for the test.
        """
        for i in range(5):
            await _create_test_user(
                async_session, username=f"paginate_{i}",
            )

        page = await UserRepository(async_session).search_users(
            "paginate", limit=2, offset=1,
        )
        assert len(page) == 2

    async def test_search_no_results(self, async_session: AsyncSession) -> None:
        """No matches returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        results = await UserRepository(async_session).search_users(
            "zzz_no_match",
        )
        assert results == []

    # ============================================================================
    # User Profile Tests
    # ============================================================================

    async def test_create_user_profile_returns_uuid(self, async_session: AsyncSession) -> None:
        """Creating a profile returns its UUID.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        profile_id = await UserRepository(async_session).create_user_profile(
            user_id=user_id,
            profile_data={"bio": "Diver", "first_name": "michael"},
        )
        assert isinstance(profile_id, uuid.UUID)

    async def test_create_user_profile_persists_fields(self, async_session: AsyncSession) -> None:
        """Profile fields are persisted correctly.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_profile(
            user_id=user_id,
            profile_data={
                "bio": "Diver",
                "first_name": "michael",
                "last_name": "Waters",
            },
        )
        profile = await UserRepository(async_session).get_user_profile(
            user_id,
        )
        assert profile is not None
        assert profile.bio == "Diver"
        assert profile.first_name == "michael"
        assert profile.last_name == "Waters"

    async def test_create_user_profile_no_data(self, async_session: AsyncSession) -> None:
        """Creating a profile with no data still succeeds.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        profile_id = await UserRepository(async_session).create_user_profile(
            user_id=user_id,
        )
        assert isinstance(profile_id, uuid.UUID)

    async def test_get_user_profile_not_found(self, async_session: AsyncSession) -> None:
        """Returns None when no profile exists for the user.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_profile(
            uuid.uuid4(),
        )
        assert result is None

    async def test_update_user_profile(self, async_session: AsyncSession) -> None:
        """Updating profile fields persists changes.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_profile(
            user_id=user_id,
            profile_data={"bio": "Old"},
        )
        await UserRepository(async_session).update_user_profile(
            user_id,
            {"bio": "New", "location": "Bonaire"},
        )
        profile = await UserRepository(async_session).get_user_profile(
            user_id,
        )
        assert profile.bio == "New"
        assert profile.location == "Bonaire"

    async def test_update_user_profile_no_profile(self, async_session: AsyncSession) -> None:
        """Updating a non-existent profile is a no-op.

        Args:
            async_session: Database session for the test.
        """
        await UserRepository(async_session).update_user_profile(
            uuid.uuid4(), {"bio": "X"},
        )
        # No exception raised — silent no-op

    # ============================================================================
    # Get User With Profile Tests
    # ============================================================================

    async def test_returns_tuple(self, async_session: AsyncSession) -> None:
        """Returns (User, UserProfile, PrivacySettings) as a tuple.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_profile(
            user_id=user_id,
            profile_data={"bio": "Hello"},
        )
        await UserRepository(async_session).create_user_privacy_settings(
            user_id=user_id,
        )

        result = await UserRepository(async_session).get_user_with_profile(
            user_id,
        )
        assert result is not None
        user, profile, privacy = result
        assert user.id == user_id
        assert profile is not None
        assert profile.bio == "Hello"
        assert privacy is not None

    async def test_returns_none_for_missing_user(self, async_session: AsyncSession) -> None:
        """Returns None when user does not exist.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_with_profile(
            uuid.uuid4(),
        )
        assert result is None

    async def test_tuple_with_missing_profile(self, async_session: AsyncSession) -> None:
        """Profile is None in the tuple when not yet created.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        result = await UserRepository(async_session).get_user_with_profile(
            user_id,
        )
        assert result is not None
        user, profile, privacy = result
        assert user.id == user_id
        assert profile is None
        assert privacy is None

    # ============================================================================
    # User Settings Tests
    # ============================================================================

    async def test_create_user_settings_defaults(self, async_session: AsyncSession) -> None:
        """Settings are created with sensible defaults.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        settings_id = await UserRepository(async_session).create_user_settings(
            user_id=user_id,
        )
        assert isinstance(settings_id, uuid.UUID)

        settings = await UserRepository(async_session).get_user_settings(
            user_id,
        )
        assert settings.preferred_units == UnitSystem.IMPERIAL
        assert settings.timezone == "UTC"
        assert settings.language == "en"

    async def test_create_user_settings_overrides(self, async_session: AsyncSession) -> None:
        """Explicit values override defaults.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_settings(
            user_id=user_id,
            settings_data={
                "preferred_units": UnitSystem.METRIC,
                "timezone": "America/New_York",
            },
        )
        settings = await UserRepository(async_session).get_user_settings(
            user_id,
        )
        assert settings.preferred_units == UnitSystem.METRIC
        assert settings.timezone == "America/New_York"

    async def test_get_user_settings_not_found(self, async_session: AsyncSession) -> None:
        """Returns None when no settings exist.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_settings(
            uuid.uuid4(),
        )
        assert result is None

    async def test_update_user_settings(self, async_session: AsyncSession) -> None:
        """Updating settings persists changes.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_settings(
            user_id=user_id,
        )
        await UserRepository(async_session).update_user_settings(
            user_id, {"language": "es"},
        )
        settings = await UserRepository(async_session).get_user_settings(
            user_id,
        )
        assert settings.language == "es"

    async def test_update_user_settings_no_settings(self, async_session: AsyncSession) -> None:
        """Updating non-existent settings is a no-op.

        Args:
            async_session: Database session for the test.
        """
        await UserRepository(async_session).update_user_settings(
            uuid.uuid4(), {"language": "fr"},
        )

    # ============================================================================
    # Privacy Settings Tests
    # ============================================================================

    async def test_create_privacy_defaults(self, async_session: AsyncSession) -> None:
        """Privacy settings are created with PUBLIC defaults.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        privacy_id = await UserRepository(async_session).create_user_privacy_settings(
            user_id=user_id,
        )
        assert isinstance(privacy_id, uuid.UUID)

        privacy = await UserRepository(async_session).get_user_privacy_settings(
            user_id,
        )
        assert privacy.profile_visibility == Visibility.PUBLIC
        assert privacy.dive_logs_visibility == Visibility.PUBLIC
        assert privacy.media_visibility == Visibility.PUBLIC
        assert privacy.stats_visibility == Visibility.PUBLIC

    async def test_create_privacy_overrides(self, async_session: AsyncSession) -> None:
        """Explicit visibility values override defaults.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_privacy_settings(
            user_id=user_id,
            privacy_data={
                "profile_visibility": Visibility.PRIVATE,
            },
        )
        privacy = await UserRepository(async_session).get_user_privacy_settings(
            user_id,
        )
        assert privacy.profile_visibility == Visibility.PRIVATE

    async def test_get_privacy_settings_not_found(self, async_session: AsyncSession) -> None:
        """Returns None when no privacy settings exist.

        Args:
            async_session: Database session for the test.
        """
        result = await UserRepository(async_session).get_user_privacy_settings(
            uuid.uuid4(),
        )
        assert result is None

    async def test_update_user_privacy_settings(self, async_session: AsyncSession) -> None:
        """Updating privacy fields persists changes.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await UserRepository(async_session).create_user_privacy_settings(
            user_id=user_id,
        )
        await UserRepository(async_session).update_user_privacy_settings(
            user_id,
            {
                "dive_logs_visibility": Visibility.PRIVATE,
                "media_visibility": Visibility.UNLISTED,
            },
        )
        privacy = await UserRepository(async_session).get_user_privacy_settings(
            user_id,
        )
        assert privacy.dive_logs_visibility == Visibility.PRIVATE
        assert privacy.media_visibility == Visibility.UNLISTED

    async def test_update_privacy_settings_no_settings(self, async_session: AsyncSession) -> None:
        """Updating non-existent privacy settings is a no-op.

        Args:
            async_session: Database session for the test.
        """
        await UserRepository(async_session).update_user_privacy_settings(
            uuid.uuid4(), {"profile_visibility": Visibility.PRIVATE},
        )
