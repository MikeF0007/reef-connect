"""Interface for the species tag repository."""

import uuid
from typing import Optional, Protocol

from common.db.models.core_models import MediaSpeciesTag


class ISpeciesTagRepository(Protocol):
    """Protocol defining the contract for species tag CRUD operations.

    Species tags represent the many-to-many relationship between media and
    species.  Each tag has a composite primary key ``(media_id, species_id)``
    — there can be at most one tag per media/species pair.
    """

    async def create_tag(
        self,
        *,
        media_id: uuid.UUID,
        species_id: uuid.UUID,
        source: str,
        model_confidence: Optional[float] = None,
    ) -> MediaSpeciesTag:
        """Create a new species tag on a media item.

        Args:
            media_id: UUID of the media item to tag.
            species_id: UUID of the species to tag with.
            source: Tag origin — ``"user"`` or ``"ml"``.
            model_confidence: Confidence score in the 0–1 range. Required
                when *source* is ``"ml"``; should be ``None`` for user tags.

        Returns:
            The newly created MediaSpeciesTag instance.

        Raises:
            sqlalchemy.exc.IntegrityError: If a tag already exists for this
                ``(media_id, species_id)`` pair (UNIQUE constraint).
        """
        ...

    async def check_tag_exists(
        self, media_id: uuid.UUID, species_id: uuid.UUID
    ) -> bool:
        """Check whether a tag already exists for a media/species pair.

        Args:
            media_id: The media UUID.
            species_id: The species UUID.

        Returns:
            ``True`` if the tag exists, ``False`` otherwise.
        """
        ...

    async def get_tags_by_ids(
        self, tag_ids: list[tuple[uuid.UUID, uuid.UUID]]
    ) -> list[MediaSpeciesTag]:
        """Retrieve tags by composite key in a single query.

        Args:
            tag_ids: List of ``(media_id, species_id)`` tuples to look up.

        Returns:
            A list of found MediaSpeciesTag instances
            (missing pairs are silently skipped).
        """
        ...

    async def get_tags_for_media(self, media_id: uuid.UUID) -> list[MediaSpeciesTag]:
        """Retrieve all species tags for a media item.

        Results are ordered by ``tagged_at`` descending.

        Args:
            media_id: The media UUID.

        Returns:
            A list of MediaSpeciesTag instances for the given media.
        """
        ...

    async def get_user_tags_for_species(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> list[MediaSpeciesTag]:
        """Retrieve all tags for a species created via a user's media.

        Returns tags where the parent media is owned by *user_id* and
        the tagged species is *species_id*.  Results are ordered by
        ``tagged_at`` descending.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.

        Returns:
            A list of MediaSpeciesTag instances.
        """
        ...

    async def delete_tag(self, media_id: uuid.UUID, species_id: uuid.UUID) -> bool:
        """Delete a species tag by its composite key.

        Args:
            media_id: The media UUID.
            species_id: The species UUID.

        Returns:
            ``True`` if the tag was deleted, ``False`` if not found.
        """
        ...

    async def delete_tags_for_media(self, media_id: uuid.UUID) -> int:
        """Delete all species tags for a media item.

        Args:
            media_id: The media UUID.

        Returns:
            The number of tags deleted.
        """
        ...
