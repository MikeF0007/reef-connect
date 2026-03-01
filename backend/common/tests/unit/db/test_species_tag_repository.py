"""Unit tests for SpeciesTagRepository.

Tests cover all CRUD operations against an in-memory SQLite database.
"""

import uuid
from decimal import Decimal
from typing import Any, Optional

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import MediaSpeciesTag, Species
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.species_tag_repository import SpeciesTagRepository
from common.db.repositories.user_repository import UserRepository
from common.types import MediaType, SpeciesTagSource


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_test_user(session: AsyncSession, **overrides: Any) -> uuid.UUID:
    """Insert a user with sensible defaults and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        overrides: Field values to override the defaults.

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


async def _create_test_species(session: AsyncSession, **overrides: Any) -> uuid.UUID:
    """Insert a species directly and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        overrides: Field values to override the defaults.

    Returns:
        The UUID of the created species.
    """
    defaults = {
        "ml_label": f"species_{uuid.uuid4().hex[:8]}",
        "scientific_name": "Testus speciesus",
        "common_name": "Test Fish",
    }
    defaults.update(overrides)
    species = Species(**defaults)
    session.add(species)
    await session.flush()
    return species.id


async def _create_test_media(
    session: AsyncSession, user_id: uuid.UUID, **overrides: Any
) -> uuid.UUID:
    """Insert a media item with sensible defaults and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        user_id: Owning user UUID.
        overrides: Field values to override the defaults.

    Returns:
        The UUID of the created media item.
    """
    defaults: dict[str, Any] = {
        "storage_key": f"uploads/{uuid.uuid4().hex}.jpg",
        "type": MediaType.IMAGE,
    }
    defaults.update(overrides)
    return await MediaRepository(session).create_media(user_id=user_id, **defaults)


async def _create_test_tag(
    session: AsyncSession,
    media_id: uuid.UUID,
    species_id: uuid.UUID,
    source: SpeciesTagSource = SpeciesTagSource.USER,
    model_confidence: Optional[float] = None,
) -> MediaSpeciesTag:
    """Create a species tag via the repository and return it.

    Args:
        session: AsyncSession to use for DB operations.
        media_id: Media UUID to tag.
        species_id: Species UUID to tag with.
        source: Tag source (USER or ML).
        model_confidence: Confidence score; required for ML tags.

    Returns:
        The created MediaSpeciesTag instance.
    """
    return await SpeciesTagRepository(session).create_tag(
        media_id=media_id,
        species_id=species_id,
        source=source,
        model_confidence=model_confidence,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSpeciesTagRepository:
    """Tests for SpeciesTagRepository covering all CRUD operations."""

    # ============================================================================
    # Create Tests
    # ============================================================================

    async def test_create_tag_returns_instance(
        self, async_session: AsyncSession
    ) -> None:
        """Creating a tag returns a MediaSpeciesTag instance.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)

        tag = await _create_test_tag(async_session, media_id, species_id)

        assert isinstance(tag, MediaSpeciesTag)

    async def test_create_tag_persists_composite_key(
        self, async_session: AsyncSession
    ) -> None:
        """Created tag has correct media_id and species_id.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)

        tag = await _create_test_tag(async_session, media_id, species_id)

        assert tag.media_id == media_id
        assert tag.species_id == species_id

    async def test_create_user_tag_persists_source(
        self, async_session: AsyncSession
    ) -> None:
        """User tag source is persisted as SpeciesTagSource.USER.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)

        tag = await _create_test_tag(
            async_session, media_id, species_id, source=SpeciesTagSource.USER
        )

        assert tag.source == SpeciesTagSource.USER

    async def test_create_ml_tag_persists_source_and_confidence(
        self, async_session: AsyncSession
    ) -> None:
        """ML tag source and model_confidence are persisted correctly.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)

        tag = await _create_test_tag(
            async_session,
            media_id,
            species_id,
            source=SpeciesTagSource.ML,
            model_confidence=0.9512,
        )

        assert tag.source == SpeciesTagSource.ML
        assert tag.model_confidence == Decimal("0.9512")

    async def test_create_user_tag_has_no_confidence(
        self, async_session: AsyncSession
    ) -> None:
        """User tag model_confidence defaults to None.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)

        tag = await _create_test_tag(async_session, media_id, species_id)

        assert tag.model_confidence is None

    async def test_create_duplicate_tag_raises_integrity_error(
        self, async_session: AsyncSession
    ) -> None:
        """Creating a duplicate (media_id, species_id) pair raises IntegrityError.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)

        await _create_test_tag(async_session, media_id, species_id)

        with pytest.raises(IntegrityError):
            await _create_test_tag(async_session, media_id, species_id)

    # ============================================================================
    # Check Exists Tests
    # ============================================================================

    async def test_check_tag_exists_returns_true_when_present(
        self, async_session: AsyncSession
    ) -> None:
        """check_tag_exists returns True for an existing tag.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        exists = await SpeciesTagRepository(async_session).check_tag_exists(
            media_id, species_id
        )

        assert exists is True

    async def test_check_tag_exists_returns_false_when_absent(
        self, async_session: AsyncSession
    ) -> None:
        """check_tag_exists returns False for a non-existent tag.

        Args:
            async_session: Database session for the test.
        """
        exists = await SpeciesTagRepository(async_session).check_tag_exists(
            uuid.uuid4(), uuid.uuid4()
        )

        assert exists is False

    async def test_check_tag_exists_wrong_species_returns_false(
        self, async_session: AsyncSession
    ) -> None:
        """check_tag_exists returns False when only media_id matches.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        other_species_id = await _create_test_species(async_session)
        exists = await SpeciesTagRepository(async_session).check_tag_exists(
            media_id, other_species_id
        )

        assert exists is False

    # ============================================================================
    # Get By IDs Tests
    # ============================================================================

    async def test_get_tags_by_ids_returns_matching_tags(
        self, async_session: AsyncSession
    ) -> None:
        """get_tags_by_ids returns all requested tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)
        await _create_test_tag(async_session, media_id, species_id_b)

        tags = await SpeciesTagRepository(async_session).get_tags_by_ids(
            [(media_id, species_id_a), (media_id, species_id_b)]
        )

        assert len(tags) == 2
        returned_species = {t.species_id for t in tags}
        assert returned_species == {species_id_a, species_id_b}

    async def test_get_tags_by_ids_skips_missing_pairs(
        self, async_session: AsyncSession
    ) -> None:
        """get_tags_by_ids silently omits non-existent composite key pairs.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        tags = await SpeciesTagRepository(async_session).get_tags_by_ids(
            [(media_id, species_id), (uuid.uuid4(), uuid.uuid4())]
        )

        assert len(tags) == 1

    async def test_get_tags_by_ids_empty_list_returns_empty(
        self, async_session: AsyncSession
    ) -> None:
        """get_tags_by_ids with an empty list returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        tags = await SpeciesTagRepository(async_session).get_tags_by_ids([])

        assert tags == []

    # ============================================================================
    # Get Tags For Media Tests
    # ============================================================================

    async def test_get_tags_for_media_returns_all_tags(
        self, async_session: AsyncSession
    ) -> None:
        """get_tags_for_media returns every tag on the media item.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)
        await _create_test_tag(async_session, media_id, species_id_b)

        tags = await SpeciesTagRepository(async_session).get_tags_for_media(media_id)

        assert len(tags) == 2

    async def test_get_tags_for_media_empty_when_no_tags(
        self, async_session: AsyncSession
    ) -> None:
        """get_tags_for_media returns an empty list when no tags exist.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)

        tags = await SpeciesTagRepository(async_session).get_tags_for_media(media_id)

        assert tags == []

    async def test_get_tags_for_media_excludes_other_media(
        self, async_session: AsyncSession
    ) -> None:
        """get_tags_for_media does not return tags from other media items.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id_a = await _create_test_media(async_session, user_id)
        media_id_b = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id_a, species_id)

        tags = await SpeciesTagRepository(async_session).get_tags_for_media(media_id_b)

        assert tags == []

    # ============================================================================
    # Get User Tags For Species Tests
    # ============================================================================

    async def test_get_user_tags_for_species_returns_matching_tags(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_tags_for_species returns tags on the user's media for the species.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        tags = await SpeciesTagRepository(async_session).get_user_tags_for_species(
            user_id, species_id
        )

        assert len(tags) == 1
        assert tags[0].media_id == media_id

    async def test_get_user_tags_for_species_excludes_other_users(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_tags_for_species ignores tags from other users' media.

        Args:
            async_session: Database session for the test.
        """
        user_id_a = await _create_test_user(async_session)
        user_id_b = await _create_test_user(async_session)
        media_id_b = await _create_test_media(async_session, user_id_b)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id_b, species_id)

        tags = await SpeciesTagRepository(async_session).get_user_tags_for_species(
            user_id_a, species_id
        )

        assert tags == []

    async def test_get_user_tags_for_species_multiple_media(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_tags_for_species aggregates across multiple media items.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id_a = await _create_test_media(async_session, user_id)
        media_id_b = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id_a, species_id)
        await _create_test_tag(async_session, media_id_b, species_id)

        tags = await SpeciesTagRepository(async_session).get_user_tags_for_species(
            user_id, species_id
        )

        assert len(tags) == 2

    async def test_get_user_tags_for_species_excludes_other_species(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_tags_for_species filters by species_id.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)

        tags = await SpeciesTagRepository(async_session).get_user_tags_for_species(
            user_id, species_id_b
        )

        assert tags == []

    async def test_get_user_tags_for_species_empty_when_none(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_tags_for_species returns empty list when user has no tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        tags = await SpeciesTagRepository(async_session).get_user_tags_for_species(
            user_id, species_id
        )

        assert tags == []

    # ============================================================================
    # Delete Tag Tests
    # ============================================================================

    async def test_delete_tag_returns_true_on_success(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tag returns True when the tag exists and is deleted.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        result = await SpeciesTagRepository(async_session).delete_tag(
            media_id, species_id
        )

        assert result is True

    async def test_delete_tag_removes_tag(self, async_session: AsyncSession) -> None:
        """Tag is no longer present after deletion.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        await SpeciesTagRepository(async_session).delete_tag(media_id, species_id)

        exists = await SpeciesTagRepository(async_session).check_tag_exists(
            media_id, species_id
        )
        assert exists is False

    async def test_delete_tag_returns_false_when_not_found(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tag returns False for a non-existent tag.

        Args:
            async_session: Database session for the test.
        """
        result = await SpeciesTagRepository(async_session).delete_tag(
            uuid.uuid4(), uuid.uuid4()
        )

        assert result is False

    async def test_delete_tag_only_removes_target_tag(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tag does not affect sibling tags on the same media.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)
        await _create_test_tag(async_session, media_id, species_id_b)

        await SpeciesTagRepository(async_session).delete_tag(media_id, species_id_a)

        exists = await SpeciesTagRepository(async_session).check_tag_exists(
            media_id, species_id_b
        )
        assert exists is True

    # ============================================================================
    # Delete Tags For Media Tests
    # ============================================================================

    async def test_delete_tags_for_media_returns_count(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tags_for_media returns the number of deleted tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)
        await _create_test_tag(async_session, media_id, species_id_b)

        count = await SpeciesTagRepository(async_session).delete_tags_for_media(
            media_id
        )

        assert count == 2

    async def test_delete_tags_for_media_removes_all_tags(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tags_for_media leaves no tags on the media item.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)
        await _create_test_tag(async_session, media_id, species_id_b)

        await SpeciesTagRepository(async_session).delete_tags_for_media(media_id)

        remaining = await SpeciesTagRepository(async_session).get_tags_for_media(
            media_id
        )
        assert remaining == []

    async def test_delete_tags_for_media_returns_zero_when_none(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tags_for_media returns 0 when no tags exist on the media.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)

        count = await SpeciesTagRepository(async_session).delete_tags_for_media(
            media_id
        )

        assert count == 0

    async def test_delete_tags_for_media_excludes_other_media(
        self, async_session: AsyncSession
    ) -> None:
        """delete_tags_for_media does not affect tags on other media items.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id_a = await _create_test_media(async_session, user_id)
        media_id_b = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id_a, species_id)
        await _create_test_tag(async_session, media_id_b, species_id)

        await SpeciesTagRepository(async_session).delete_tags_for_media(media_id_a)

        exists = await SpeciesTagRepository(async_session).check_tag_exists(
            media_id_b, species_id
        )
        assert exists is True
