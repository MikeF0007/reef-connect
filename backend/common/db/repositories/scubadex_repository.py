"""DB-based IScubaDexRepository implementation.

Provides async CRUD and reconciliation operations for ScubadexEntry records.
"""

import uuid
from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import Media, MediaSpeciesTag, ScubadexEntry
from common.db.repositories.interfaces import IMediaRepository, IScubaDexRepository


class ScubaDexRepository(IScubaDexRepository):
    """Provides async operations for managing the ScubaDex materialized view.

    The ScubaDex is maintained event-driven: ``record_species_encounter`` and
    ``remove_species_encounter`` handle incremental updates, while
    ``reconcile_user_dex`` performs a full rebuild from the source of truth.

    Attributes:
        session: AsyncSession used for all DB operations.
        media_repo: IMediaRepository reference used during reconciliation.
    """

    def __init__(self, session: AsyncSession, media_repo: IMediaRepository) -> None:
        self.session = session
        self.media_repo = media_repo

    # ================ Encounter Mutations ================

    async def record_species_encounter(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> None:
        """Record a new encounter with a species for a user.

        Creates a new ScubadexEntry with ``times_encountered = 1`` if none
        exists; otherwise increments the existing count.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.
        """
        entry = await self._get_entry(user_id, species_id)
        if entry is None:
            entry = ScubadexEntry(
                user_id=user_id,
                species_id=species_id,
                times_encountered=1,
                date_first_encountered=date.today(),
            )
            self.session.add(entry)
        else:
            entry.times_encountered += 1
        await self.session.flush()

    async def remove_species_encounter(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> None:
        """Remove one encounter record for a species.

        Decrements ``times_encountered`` by one.  If the count reaches zero
        the entry is deleted (FR-1.19: no remaining evidence).

        Args:
            user_id: The user UUID.
            species_id: The species UUID.
        """
        entry = await self._get_entry(user_id, species_id)
        if entry is None:
            return
        if entry.times_encountered <= 1:
            await self.session.delete(entry)
        else:
            entry.times_encountered -= 1
        await self.session.flush()

    async def clear_species_encounters(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> None:
        """Remove all encounters for a species by deleting the entry.

        No-op if no entry exists.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.
        """
        entry = await self._get_entry(user_id, species_id)
        if entry is not None:
            await self.session.delete(entry)
            await self.session.flush()

    # ================ Encounter Reads ================

    async def get_encounter_count(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> int:
        """Return the current materialized encounter count for a species.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.

        Returns:
            ``times_encountered`` for the entry, or ``0`` if not found.
        """
        entry = await self._get_entry(user_id, species_id)
        return entry.times_encountered if entry is not None else 0

    async def get_user_dex_entries(self, user_id: uuid.UUID) -> list[ScubadexEntry]:
        """Return all ScubadexEntry instances for a user.

        Results are ordered by ``date_first_encountered`` ascending so callers
        receive the user's discovery history in chronological order.

        Args:
            user_id: The user UUID.

        Returns:
            A list of ScubadexEntry ORM objects.
        """
        from sqlalchemy import asc

        stmt = (
            select(ScubadexEntry)
            .where(ScubadexEntry.user_id == user_id)
            .order_by(asc(ScubadexEntry.date_first_encountered))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_species_encounters(
        self, user_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int]]:
        """Return all species encountered by a user with their counts.

        Args:
            user_id: The user UUID.

        Returns:
            A list of ``(species_id, times_encountered)`` tuples.
        """
        stmt = select(ScubadexEntry).where(ScubadexEntry.user_id == user_id)
        result = await self.session.execute(stmt)
        return [(e.species_id, e.times_encountered) for e in result.scalars().all()]

    async def get_species_for_media(
        self, media_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, uuid.UUID]]:
        """Return all species associated with a media item.

        Args:
            media_id: The media UUID.

        Returns:
            A list of ``(media_id, species_id)`` tuples.
        """
        stmt = select(MediaSpeciesTag).where(MediaSpeciesTag.media_id == media_id)
        result = await self.session.execute(stmt)
        return [(tag.media_id, tag.species_id) for tag in result.scalars().all()]

    # ================ Reconciliation ================

    async def reconcile_user_dex(self, user_id: uuid.UUID) -> None:
        """Rebuild the user's ScubaDex from the source of truth.

        Scans all ``media_species_tags`` for media owned by *user_id*,
        recomputes encounter counts and first-encounter dates, upserts
        entries as needed, and deletes any stale entries.

        Args:
            user_id: The user UUID.
        """
        # 1. Fetch all species tags across user's media in one query.
        stmt = (
            select(MediaSpeciesTag)
            .join(Media, Media.id == MediaSpeciesTag.media_id)
            .where(Media.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        all_tags = result.scalars().all()

        # 2. Group by species: count occurrences and find earliest tagged_at.
        species_tags: dict[uuid.UUID, list[MediaSpeciesTag]] = defaultdict(list)
        for tag in all_tags:
            species_tags[tag.species_id].append(tag)

        # 3. Load current dex entries indexed by species_id.
        current_stmt = select(ScubadexEntry).where(ScubadexEntry.user_id == user_id)
        current_result = await self.session.execute(current_stmt)
        current: dict[uuid.UUID, ScubadexEntry] = {
            e.species_id: e for e in current_result.scalars().all()
        }

        # 4. Upsert an entry for every species present in the tags.
        for species_id, tags in species_tags.items():
            count = len(tags)
            first_date = min(t.tagged_at for t in tags).date()
            if species_id in current:
                entry = current[species_id]
                entry.times_encountered = count
                entry.date_first_encountered = first_date
            else:
                self.session.add(
                    ScubadexEntry(
                        user_id=user_id,
                        species_id=species_id,
                        times_encountered=count,
                        date_first_encountered=first_date,
                    )
                )

        # 5. Delete entries whose species no longer have any tags.
        live_species = set(species_tags.keys())
        for species_id, entry in current.items():
            if species_id not in live_species:
                await self.session.delete(entry)

        await self.session.flush()

    # ================ Helpers ================

    async def _get_entry(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> ScubadexEntry | None:
        """Fetch a single ScubadexEntry by (user_id, species_id), or None.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.

        Returns:
            The matching ScubadexEntry, or ``None`` if not found.
        """
        stmt = select(ScubadexEntry).where(
            ScubadexEntry.user_id == user_id,
            ScubadexEntry.species_id == species_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
