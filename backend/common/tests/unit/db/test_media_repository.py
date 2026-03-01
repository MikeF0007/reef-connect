"""Unit tests for MediaRepository.

Tests cover all CRUD operations against an in-memory SQLite database.
"""

import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import Media, MediaSpeciesTag, Species
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.user_repository import UserRepository
from common.types import MediaStatus, MediaType, SpeciesTagSource


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
) -> None:
    """Insert a species tag directly into the session.

    Args:
        session: AsyncSession to use for DB operations.
        media_id: Media UUID to tag.
        species_id: Species UUID to tag with.
        source: Tag source (USER or ML).
    """
    tag = MediaSpeciesTag(media_id=media_id, species_id=species_id, source=source)
    session.add(tag)
    await session.flush()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMediaRepository:
    """Tests for MediaRepository covering all CRUD operations."""

    # ============================================================================
    # Create Tests
    # ============================================================================

    async def test_create_media_returns_uuid(self, async_session: AsyncSession) -> None:
        """Creating a media item returns a UUID.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await MediaRepository(async_session).create_media(
            user_id=user_id,
            storage_key="uploads/photo.jpg",
            type=MediaType.IMAGE,
        )
        assert isinstance(media_id, uuid.UUID)

    async def test_create_media_status_defaults_to_pending(
        self, async_session: AsyncSession
    ) -> None:
        """New media items are created with PENDING status.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media.status == MediaStatus.PENDING

    async def test_create_media_persists_required_fields(
        self, async_session: AsyncSession
    ) -> None:
        """All required fields are persisted correctly.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await MediaRepository(async_session).create_media(
            user_id=user_id,
            storage_key="uploads/video.mp4",
            type=MediaType.VIDEO,
        )
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media.user_id == user_id
        assert media.storage_key == "uploads/video.mp4"
        assert media.type == MediaType.VIDEO

    async def test_create_media_persists_optional_fields(
        self, async_session: AsyncSession
    ) -> None:
        """Optional kwargs are persisted when provided.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await MediaRepository(async_session).create_media(
            user_id=user_id,
            storage_key="uploads/photo.jpg",
            type=MediaType.IMAGE,
            description="A beautiful reef photo",
            mime_type="image/jpeg",
        )
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media.description == "A beautiful reef photo"
        assert media.mime_type == "image/jpeg"

    # ============================================================================
    # Lookup Tests
    # ============================================================================

    async def test_get_media_by_id(self, async_session: AsyncSession) -> None:
        """Lookup by ID returns the correct media item.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media is not None
        assert media.id == media_id

    async def test_get_media_by_id_not_found(self, async_session: AsyncSession) -> None:
        """Lookup by non-existent ID returns None.

        Args:
            async_session: Database session for the test.
        """
        result = await MediaRepository(async_session).get_media_by_id(uuid.uuid4())
        assert result is None

    async def test_get_media_by_ids(self, async_session: AsyncSession) -> None:
        """Batch lookup returns only existing media items.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        id1 = await _create_test_media(async_session, user_id)
        id2 = await _create_test_media(async_session, user_id)
        missing = uuid.uuid4()

        results = await MediaRepository(async_session).get_media_by_ids(
            [id1, id2, missing]
        )
        found_ids = {m.id for m in results}
        assert id1 in found_ids
        assert id2 in found_ids
        assert missing not in found_ids

    async def test_get_media_by_ids_empty_list(
        self, async_session: AsyncSession
    ) -> None:
        """Empty input returns an empty list without hitting the DB.

        Args:
            async_session: Database session for the test.
        """
        results = await MediaRepository(async_session).get_media_by_ids([])
        assert results == []

    # ============================================================================
    # Get By User Tests
    # ============================================================================

    async def test_get_media_by_user_returns_only_that_users_media(
        self, async_session: AsyncSession
    ) -> None:
        """Only the queried user's media items are returned.

        Args:
            async_session: Database session for the test.
        """
        user_a = await _create_test_user(async_session)
        user_b = await _create_test_user(async_session)
        await _create_test_media(async_session, user_a)
        await _create_test_media(async_session, user_b)

        results = await MediaRepository(async_session).get_media_by_user(user_a)
        assert len(results) == 1
        assert results[0].user_id == user_a

    async def test_get_media_by_user_filter_by_type(
        self, async_session: AsyncSession
    ) -> None:
        """Results are filtered to the requested media type.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_media(async_session, user_id, type=MediaType.IMAGE)
        await _create_test_media(async_session, user_id, type=MediaType.VIDEO)

        images = await MediaRepository(async_session).get_media_by_user(
            user_id, media_type=MediaType.IMAGE
        )
        assert len(images) == 1
        assert images[0].type == MediaType.IMAGE

    async def test_get_media_by_user_pagination(
        self, async_session: AsyncSession
    ) -> None:
        """Limit and offset control the result window.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        for _ in range(5):
            await _create_test_media(async_session, user_id)

        page = await MediaRepository(async_session).get_media_by_user(
            user_id, limit=2, offset=1
        )
        assert len(page) == 2

    async def test_get_media_by_user_empty(self, async_session: AsyncSession) -> None:
        """A user with no media returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        results = await MediaRepository(async_session).get_media_by_user(user_id)
        assert results == []

    # ============================================================================
    # Get By Dive Log Tests
    # ============================================================================

    async def test_get_media_by_dive_log_returns_linked_media(
        self, async_session: AsyncSession
    ) -> None:
        """Media linked to a dive log is returned.

        Args:
            async_session: Database session for the test.
        """
        from common.db.repositories.dive_log_repository import DiveLogRepository
        from datetime import date

        user_id = await _create_test_user(async_session)
        dive_log_id = await DiveLogRepository(async_session).create_dive_log(
            user_id=user_id,
            dive_date=date(2024, 6, 15),
            dive_title="Test Dive",
            dive_site="Blue Corner",
            duration_minutes=45,
        )
        media_id = await _create_test_media(
            async_session, user_id, dive_log_id=dive_log_id
        )
        await _create_test_media(async_session, user_id)  # unlinked media

        results = await MediaRepository(async_session).get_media_by_dive_log(
            dive_log_id
        )
        assert len(results) == 1
        assert results[0].id == media_id

    async def test_get_media_by_dive_log_filter_by_type(
        self, async_session: AsyncSession
    ) -> None:
        """Results are filtered to the requested media type.

        Args:
            async_session: Database session for the test.
        """
        from common.db.repositories.dive_log_repository import DiveLogRepository
        from datetime import date

        user_id = await _create_test_user(async_session)
        dive_log_id = await DiveLogRepository(async_session).create_dive_log(
            user_id=user_id,
            dive_date=date(2024, 6, 15),
            dive_title="Test Dive",
            dive_site="Blue Corner",
            duration_minutes=45,
        )
        await _create_test_media(
            async_session, user_id, dive_log_id=dive_log_id, type=MediaType.IMAGE
        )
        await _create_test_media(
            async_session, user_id, dive_log_id=dive_log_id, type=MediaType.VIDEO
        )

        videos = await MediaRepository(async_session).get_media_by_dive_log(
            dive_log_id, media_type=MediaType.VIDEO
        )
        assert len(videos) == 1
        assert videos[0].type == MediaType.VIDEO

    async def test_get_media_by_dive_log_empty(
        self, async_session: AsyncSession
    ) -> None:
        """A dive log with no media returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        results = await MediaRepository(async_session).get_media_by_dive_log(
            uuid.uuid4()
        )
        assert results == []

    # ============================================================================
    # Get By Species Tag Tests
    # ============================================================================

    async def test_get_media_by_species_tag_returns_tagged_media(
        self, async_session: AsyncSession
    ) -> None:
        """Media tagged with a species is returned.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        media_id = await _create_test_media(async_session, user_id)
        untagged_id = await _create_test_media(async_session, user_id)  # noqa: F841
        await _create_test_tag(async_session, media_id, species_id)

        results = await MediaRepository(async_session).get_media_by_species_tag(
            user_id, species_id
        )
        assert len(results) == 1
        assert results[0].id == media_id

    async def test_get_media_by_species_tag_scoped_to_user(
        self, async_session: AsyncSession
    ) -> None:
        """Results are scoped to the specified user.

        Args:
            async_session: Database session for the test.
        """
        user_a = await _create_test_user(async_session)
        user_b = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        media_a = await _create_test_media(async_session, user_a)
        media_b = await _create_test_media(async_session, user_b)
        await _create_test_tag(async_session, media_a, species_id)
        await _create_test_tag(async_session, media_b, species_id)

        results = await MediaRepository(async_session).get_media_by_species_tag(
            user_a, species_id
        )
        assert len(results) == 1
        assert results[0].user_id == user_a

    async def test_get_media_by_species_tag_filter_by_type(
        self, async_session: AsyncSession
    ) -> None:
        """Results are filtered to the requested media type.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        image_id = await _create_test_media(
            async_session, user_id, type=MediaType.IMAGE
        )
        video_id = await _create_test_media(
            async_session, user_id, type=MediaType.VIDEO
        )
        await _create_test_tag(async_session, image_id, species_id)
        await _create_test_tag(async_session, video_id, species_id)

        images = await MediaRepository(async_session).get_media_by_species_tag(
            user_id, species_id, media_type=MediaType.IMAGE
        )
        assert len(images) == 1
        assert images[0].type == MediaType.IMAGE

    async def test_get_media_by_species_tag_empty(
        self, async_session: AsyncSession
    ) -> None:
        """No matching tags returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        results = await MediaRepository(async_session).get_media_by_species_tag(
            user_id, species_id
        )
        assert results == []

    # ============================================================================
    # Get Species Tags For Media Tests
    # ============================================================================

    async def test_get_species_tags_for_media_returns_all_tags(
        self, async_session: AsyncSession
    ) -> None:
        """All species tags for a media item are returned.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_a = await _create_test_species(async_session)
        species_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_a)
        await _create_test_tag(async_session, media_id, species_b)

        tags = await MediaRepository(async_session).get_species_tags_for_media(media_id)
        assert len(tags) == 2

    async def test_get_species_tags_for_media_empty(
        self, async_session: AsyncSession
    ) -> None:
        """A media item with no tags returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)

        tags = await MediaRepository(async_session).get_species_tags_for_media(media_id)
        assert tags == []

    # ============================================================================
    # Update Status Tests
    # ============================================================================

    async def test_update_media_status_persists_change(
        self, async_session: AsyncSession
    ) -> None:
        """Updated status is persisted.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)

        await MediaRepository(async_session).update_media_status(
            media_id, MediaStatus.PROCESSED
        )
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media.status == MediaStatus.PROCESSED

    async def test_update_media_status_not_found_is_noop(
        self, async_session: AsyncSession
    ) -> None:
        """Updating status on a non-existent media item is a silent no-op.

        Args:
            async_session: Database session for the test.
        """
        await MediaRepository(async_session).update_media_status(
            uuid.uuid4(), MediaStatus.FAILED
        )
        # No exception raised — silent no-op

    # ============================================================================
    # Update Details Tests
    # ============================================================================

    async def test_update_media_details_persists_changes(
        self, async_session: AsyncSession
    ) -> None:
        """Updated details are persisted.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)

        await MediaRepository(async_session).update_media_details(
            media_id, {"description": "Updated description", "mime_type": "image/png"}
        )
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media.description == "Updated description"
        assert media.mime_type == "image/png"

    async def test_update_media_details_clears_optional_field(
        self, async_session: AsyncSession
    ) -> None:
        """Setting an optional field to None clears it.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await MediaRepository(async_session).create_media(
            user_id=user_id,
            storage_key="uploads/photo.jpg",
            type=MediaType.IMAGE,
            description="A photo",
        )
        await MediaRepository(async_session).update_media_details(
            media_id, {"description": None}
        )
        media = await MediaRepository(async_session).get_media_by_id(media_id)
        assert media.description is None

    async def test_update_media_details_not_found_is_noop(
        self, async_session: AsyncSession
    ) -> None:
        """Updating details on a non-existent media item is a silent no-op.

        Args:
            async_session: Database session for the test.
        """
        await MediaRepository(async_session).update_media_details(
            uuid.uuid4(), {"description": "Ghost"}
        )
        # No exception raised — silent no-op

    # ============================================================================
    # Delete Tests
    # ============================================================================

    async def test_delete_media_returns_true(self, async_session: AsyncSession) -> None:
        """Deleting an existing media item returns True.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        result = await MediaRepository(async_session).delete_media(media_id)
        assert result is True

    async def test_delete_media_removes_from_db(
        self, async_session: AsyncSession
    ) -> None:
        """After deletion the media item is no longer found.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        await MediaRepository(async_session).delete_media(media_id)
        assert await MediaRepository(async_session).get_media_by_id(media_id) is None

    async def test_delete_media_not_found(self, async_session: AsyncSession) -> None:
        """Deleting a non-existent media item returns False.

        Args:
            async_session: Database session for the test.
        """
        result = await MediaRepository(async_session).delete_media(uuid.uuid4())
        assert result is False

    async def test_delete_media_cascades_species_tags(
        self, async_session: AsyncSession
    ) -> None:
        """Deleting a media item removes its species tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        media_id = await _create_test_media(async_session, user_id)
        await _create_test_tag(async_session, media_id, species_id)

        tags_before = await MediaRepository(async_session).get_species_tags_for_media(
            media_id
        )
        assert len(tags_before) == 1

        await MediaRepository(async_session).delete_media(media_id)

        tags_after = await MediaRepository(async_session).get_species_tags_for_media(
            media_id
        )
        assert tags_after == []
