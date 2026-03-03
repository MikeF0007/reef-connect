"""Unit tests for ScubaDexRepository.

Tests cover all encounter mutation, read, and reconciliation operations
against an in-memory SQLite database.
"""

import uuid
from datetime import date, timedelta
from typing import Any

from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import MediaSpeciesTag, ScubadexEntry, Species
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.scubadex_repository import ScubaDexRepository
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


async def _create_test_species(session: AsyncSession) -> uuid.UUID:
    """Insert a species and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.

    Returns:
        The UUID of the created species.
    """
    species = Species(
        ml_label=f"species_{uuid.uuid4().hex[:8]}",
        scientific_name="Testus speciesus",
        common_name="Test Fish",
    )
    session.add(species)
    await session.flush()
    return species.id


async def _create_test_media(session: AsyncSession, user_id: uuid.UUID) -> uuid.UUID:
    """Insert a media item and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        user_id: Owning user UUID.

    Returns:
        The UUID of the created media item.
    """
    return await MediaRepository(session).create_media(
        user_id=user_id,
        storage_key=f"uploads/{uuid.uuid4().hex}.jpg",
        type=MediaType.IMAGE,
    )


async def _create_test_tag(
    session: AsyncSession, media_id: uuid.UUID, species_id: uuid.UUID
) -> None:
    """Insert a species tag directly.

    Args:
        session: AsyncSession to use for DB operations.
        media_id: Media UUID to tag.
        species_id: Species UUID to tag with.
    """
    tag = MediaSpeciesTag(
        media_id=media_id,
        species_id=species_id,
        source=SpeciesTagSource.USER,
    )
    session.add(tag)
    await session.flush()


def _make_repo(session: AsyncSession) -> ScubaDexRepository:
    """Construct a ScubaDexRepository backed by the given session.

    Args:
        session: AsyncSession to inject.

    Returns:
        A ScubaDexRepository instance.
    """
    return ScubaDexRepository(session, MediaRepository(session))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestScubaDexRepository:
    """Tests for ScubaDexRepository covering all operations."""

    # ============================================================================
    # record_species_encounter Tests
    # ============================================================================

    async def test_record_creates_entry_when_absent(
        self, async_session: AsyncSession
    ) -> None:
        """record_species_encounter creates a new entry with count 1.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        await _make_repo(async_session).record_species_encounter(user_id, species_id)

        count = await _make_repo(async_session).get_encounter_count(user_id, species_id)
        assert count == 1

    async def test_record_increments_existing_entry(
        self, async_session: AsyncSession
    ) -> None:
        """record_species_encounter increments an existing entry's count.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)

        await repo.record_species_encounter(user_id, species_id)
        await repo.record_species_encounter(user_id, species_id)

        count = await repo.get_encounter_count(user_id, species_id)
        assert count == 2

    async def test_record_sets_date_first_encountered(
        self, async_session: AsyncSession
    ) -> None:
        """record_species_encounter sets date_first_encountered on new entry.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        await _make_repo(async_session).record_species_encounter(user_id, species_id)

        stmt_result = await async_session.execute(
            sa_select(ScubadexEntry).where(
                ScubadexEntry.user_id == user_id,
                ScubadexEntry.species_id == species_id,
            )
        )
        entry = stmt_result.scalar_one()
        assert entry.date_first_encountered == date.today()

    async def test_record_does_not_change_date_on_subsequent_calls(
        self, async_session: AsyncSession
    ) -> None:
        """record_species_encounter does not overwrite date_first_encountered.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id)

        # Manually set first date to yesterday to simulate an older entry
        result = await async_session.execute(
            sa_select(ScubadexEntry).where(
                ScubadexEntry.user_id == user_id,
                ScubadexEntry.species_id == species_id,
            )
        )
        entry = result.scalar_one()
        yesterday = date.today() - timedelta(days=1)
        entry.date_first_encountered = yesterday
        await async_session.flush()

        await repo.record_species_encounter(user_id, species_id)

        result2 = await async_session.execute(
            sa_select(ScubadexEntry).where(
                ScubadexEntry.user_id == user_id,
                ScubadexEntry.species_id == species_id,
            )
        )
        entry2 = result2.scalar_one()
        assert entry2.date_first_encountered == yesterday

    # ============================================================================
    # remove_species_encounter Tests
    # ============================================================================

    async def test_remove_decrements_count(self, async_session: AsyncSession) -> None:
        """remove_species_encounter decrements times_encountered by one.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id)
        await repo.record_species_encounter(user_id, species_id)

        await repo.remove_species_encounter(user_id, species_id)

        assert await repo.get_encounter_count(user_id, species_id) == 1

    async def test_remove_deletes_entry_at_zero(
        self, async_session: AsyncSession
    ) -> None:
        """remove_species_encounter deletes the entry when count reaches zero.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id)

        await repo.remove_species_encounter(user_id, species_id)

        assert await repo.get_encounter_count(user_id, species_id) == 0

    async def test_remove_is_noop_when_absent(
        self, async_session: AsyncSession
    ) -> None:
        """remove_species_encounter is a no-op when no entry exists.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        # Should not raise
        await _make_repo(async_session).remove_species_encounter(user_id, species_id)

        assert (
            await _make_repo(async_session).get_encounter_count(user_id, species_id)
            == 0
        )

    # ============================================================================
    # clear_species_encounters Tests
    # ============================================================================

    async def test_clear_deletes_entry(self, async_session: AsyncSession) -> None:
        """clear_species_encounters removes the entry entirely.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id)
        await repo.record_species_encounter(user_id, species_id)

        await repo.clear_species_encounters(user_id, species_id)

        assert await repo.get_encounter_count(user_id, species_id) == 0

    async def test_clear_is_noop_when_absent(self, async_session: AsyncSession) -> None:
        """clear_species_encounters is a no-op when no entry exists.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        # Should not raise
        await _make_repo(async_session).clear_species_encounters(user_id, species_id)

    async def test_clear_only_removes_target_species(
        self, async_session: AsyncSession
    ) -> None:
        """clear_species_encounters does not affect other species entries.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id_a)
        await repo.record_species_encounter(user_id, species_id_b)

        await repo.clear_species_encounters(user_id, species_id_a)

        assert await repo.get_encounter_count(user_id, species_id_b) == 1

    # ============================================================================
    # get_encounter_count Tests
    # ============================================================================

    async def test_get_encounter_count_returns_zero_when_absent(
        self, async_session: AsyncSession
    ) -> None:
        """get_encounter_count returns 0 for a user with no entry.

        Args:
            async_session: Database session for the test.
        """
        count = await _make_repo(async_session).get_encounter_count(
            uuid.uuid4(), uuid.uuid4()
        )

        assert count == 0

    async def test_get_encounter_count_returns_correct_value(
        self, async_session: AsyncSession
    ) -> None:
        """get_encounter_count returns the persisted times_encountered value.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        for _ in range(5):
            await repo.record_species_encounter(user_id, species_id)

        count = await repo.get_encounter_count(user_id, species_id)

        assert count == 5

    # ============================================================================
    # get_user_species_encounters Tests
    # ============================================================================

    async def test_get_user_species_encounters_returns_all_entries(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_species_encounters returns all (species_id, count) pairs.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id_a)
        await repo.record_species_encounter(user_id, species_id_a)
        await repo.record_species_encounter(user_id, species_id_b)

        encounters = await repo.get_user_species_encounters(user_id)

        assert len(encounters) == 2
        counts = dict(encounters)
        assert counts[species_id_a] == 2
        assert counts[species_id_b] == 1

    async def test_get_user_species_encounters_empty_when_none(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_species_encounters returns an empty list for a new user.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)

        encounters = await _make_repo(async_session).get_user_species_encounters(
            user_id
        )

        assert encounters == []

    async def test_get_user_species_encounters_excludes_other_users(
        self, async_session: AsyncSession
    ) -> None:
        """get_user_species_encounters does not include other users' entries.

        Args:
            async_session: Database session for the test.
        """
        user_id_a = await _create_test_user(async_session)
        user_id_b = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id_b, species_id)

        encounters = await repo.get_user_species_encounters(user_id_a)

        assert encounters == []

    # ============================================================================
    # get_species_for_media Tests
    # ============================================================================

    async def test_get_species_for_media_returns_tuples(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_for_media returns (media_id, species_id) tuples.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        pairs = await _make_repo(async_session).get_species_for_media(media_id)

        assert len(pairs) == 1
        assert pairs[0] == (media_id, species_id)

    async def test_get_species_for_media_returns_all_tags(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_for_media returns a tuple for each tag on the media.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id_a = await _create_test_species(async_session)
        species_id_b = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id_a)
        await _create_test_tag(async_session, media_id, species_id_b)

        pairs = await _make_repo(async_session).get_species_for_media(media_id)

        assert len(pairs) == 2

    async def test_get_species_for_media_empty_when_no_tags(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_for_media returns an empty list when media has no tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)

        pairs = await _make_repo(async_session).get_species_for_media(media_id)

        assert pairs == []

    # ============================================================================
    # reconcile_user_dex Tests
    # ============================================================================

    async def test_reconcile_creates_entries_from_tags(
        self, async_session: AsyncSession
    ) -> None:
        """reconcile_user_dex creates ScubadexEntry rows from species tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        await _make_repo(async_session).reconcile_user_dex(user_id)

        count = await _make_repo(async_session).get_encounter_count(user_id, species_id)
        assert count == 1

    async def test_reconcile_counts_multiple_tags(
        self, async_session: AsyncSession
    ) -> None:
        """reconcile_user_dex counts all tags for each species correctly.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id_a = await _create_test_media(async_session, user_id)
        media_id_b = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id_a, species_id)
        await _create_test_tag(async_session, media_id_b, species_id)

        await _make_repo(async_session).reconcile_user_dex(user_id)

        count = await _make_repo(async_session).get_encounter_count(user_id, species_id)
        assert count == 2

    async def test_reconcile_updates_stale_count(
        self, async_session: AsyncSession
    ) -> None:
        """reconcile_user_dex corrects a stale times_encountered value.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        media_id = await _create_test_media(async_session, user_id)
        species_id = await _create_test_species(async_session)
        await _create_test_tag(async_session, media_id, species_id)

        # Manually insert a stale entry with wrong count
        async_session.add(
            ScubadexEntry(
                user_id=user_id,
                species_id=species_id,
                times_encountered=99,
                date_first_encountered=date.today(),
            )
        )
        await async_session.flush()

        await _make_repo(async_session).reconcile_user_dex(user_id)

        count = await _make_repo(async_session).get_encounter_count(user_id, species_id)
        assert count == 1

    async def test_reconcile_deletes_stale_entries(
        self, async_session: AsyncSession
    ) -> None:
        """reconcile_user_dex removes entries with no supporting tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)

        # Insert a dex entry with no corresponding tag
        async_session.add(
            ScubadexEntry(
                user_id=user_id,
                species_id=species_id,
                times_encountered=3,
                date_first_encountered=date.today(),
            )
        )
        await async_session.flush()

        await _make_repo(async_session).reconcile_user_dex(user_id)

        count = await _make_repo(async_session).get_encounter_count(user_id, species_id)
        assert count == 0

    async def test_reconcile_excludes_other_users(
        self, async_session: AsyncSession
    ) -> None:
        """reconcile_user_dex does not affect other users' dex entries.

        Args:
            async_session: Database session for the test.
        """
        user_id_a = await _create_test_user(async_session)
        user_id_b = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        media_id_b = await _create_test_media(async_session, user_id_b)
        await _create_test_tag(async_session, media_id_b, species_id)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id_b, species_id)

        await repo.reconcile_user_dex(user_id_a)

        # User B's entry should be untouched
        assert await repo.get_encounter_count(user_id_b, species_id) == 1

    async def test_reconcile_no_tags_clears_entire_dex(
        self, async_session: AsyncSession
    ) -> None:
        """reconcile_user_dex removes all entries when user has no tags.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        species_id = await _create_test_species(async_session)
        repo = _make_repo(async_session)
        await repo.record_species_encounter(user_id, species_id)

        await repo.reconcile_user_dex(user_id)

        encounters = await repo.get_user_species_encounters(user_id)
        assert encounters == []
