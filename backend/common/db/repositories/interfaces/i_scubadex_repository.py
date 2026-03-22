"""Interface for the ScubaDex repository."""

import uuid
from typing import Protocol


class IScubaDexRepository(Protocol):
    """Protocol defining the contract for ScubaDex materialized data management.

    The ScubaDex is a denormalized, event-driven materialized view of
    each user's species encounter history.  It is not the source of truth
    — ``reconcile_user_dex`` can rebuild it from ``media_species_tags``
    at any time.
    """

    async def record_species_encounter(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> None:
        """Record a new encounter with a species for a user.

        If the user has no existing entry for this species, creates one with
        ``times_encountered = 1`` and ``date_first_encountered = today``.
        Otherwise increments ``times_encountered`` by one.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.
        """
        ...

    async def remove_species_encounter(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> None:
        """Remove one encounter record for a species.

        Decrements ``times_encountered`` by one.  When the count reaches
        zero the entry is deleted entirely (FR-1.19).

        Args:
            user_id: The user UUID.
            species_id: The species UUID.
        """
        ...

    async def clear_species_encounters(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> None:
        """Remove all encounter records for a species by deleting the entry.

        No-op if the entry does not exist.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.
        """
        ...

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
        ...

    async def get_user_dex_entries(self, user_id: uuid.UUID) -> list:
        """Return all ScubadexEntry instances for a user.

        Args:
            user_id: The user UUID.

        Returns:
            A list of ScubadexEntry ORM objects, ordered by
            ``date_first_encountered`` ascending.
        """
        ...

    async def get_user_species_encounters(
        self, user_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int]]:
        """Return all species encountered by a user with their counts.

        Args:
            user_id: The user UUID.

        Returns:
            A list of ``(species_id, times_encountered)`` tuples.
        """
        ...

    async def get_species_for_media(
        self, media_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, uuid.UUID]]:
        """Return all species associated with a media item.

        Args:
            media_id: The media UUID.

        Returns:
            A list of ``(media_id, species_id)`` tuples from the
            ``media_species_tags`` table.
        """
        ...

    async def reconcile_user_dex(self, user_id: uuid.UUID) -> None:
        """Rebuild the user's ScubaDex from the source of truth.

        Recomputes ``times_encountered`` and ``date_first_encountered`` for
        every species by scanning ``media_species_tags`` for all media owned
        by *user_id*.  Upserts entries that exist and deletes entries whose
        species no longer have any supporting tags.

        This ensures full consistency after any data mutation (tag removal,
        media deletion) and should be run periodically as a background job.

        Args:
            user_id: The user UUID.
        """
        ...
