"""DB-based ISpeciesTagRepository implementation.

Provides async CRUD operations for MediaSpeciesTag entries.
"""

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, delete, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import Media, MediaSpeciesTag
from common.db.repositories.interfaces import ISpeciesTagRepository
from common.types import SpeciesTagSource


class SpeciesTagRepository(ISpeciesTagRepository):
    """Provides async CRUD operations for MediaSpeciesTag entries.

    Attributes:
        session: AsyncSession used for all DB operations, ensuring
            transaction consistency across method calls.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ================ Species Tag CRUD ================

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
        tag = MediaSpeciesTag(
            media_id=media_id,
            species_id=species_id,
            source=source,
            model_confidence=(
                Decimal(str(model_confidence)) if model_confidence is not None else None
            ),
        )
        self.session.add(tag)
        await self.session.flush()
        return tag

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
        stmt = select(MediaSpeciesTag).where(
            MediaSpeciesTag.media_id == media_id,
            MediaSpeciesTag.species_id == species_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

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
        if not tag_ids:
            return []
        conditions = [
            and_(
                MediaSpeciesTag.media_id == media_id,
                MediaSpeciesTag.species_id == species_id,
            )
            for media_id, species_id in tag_ids
        ]
        stmt = select(MediaSpeciesTag).where(or_(*conditions))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_tags_for_media(self, media_id: uuid.UUID) -> list[MediaSpeciesTag]:
        """Retrieve all species tags for a media item.

        Results are ordered by ``tagged_at`` descending.

        Args:
            media_id: The media UUID.

        Returns:
            A list of MediaSpeciesTag instances for the given media.
        """
        stmt = (
            select(MediaSpeciesTag)
            .where(MediaSpeciesTag.media_id == media_id)
            .order_by(desc(MediaSpeciesTag.tagged_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_tags_for_species(
        self, user_id: uuid.UUID, species_id: uuid.UUID
    ) -> list[MediaSpeciesTag]:
        """Retrieve all tags for a species created via a user's media.

        Args:
            user_id: The user UUID.
            species_id: The species UUID.

        Returns:
            A list of MediaSpeciesTag instances ordered by ``tagged_at``
            descending.
        """
        stmt = (
            select(MediaSpeciesTag)
            .join(Media, Media.id == MediaSpeciesTag.media_id)
            .where(
                Media.user_id == user_id,
                MediaSpeciesTag.species_id == species_id,
            )
            .order_by(desc(MediaSpeciesTag.tagged_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_tag(self, media_id: uuid.UUID, species_id: uuid.UUID) -> bool:
        """Delete a species tag by its composite key.

        Args:
            media_id: The media UUID.
            species_id: The species UUID.

        Returns:
            ``True`` if the tag was deleted, ``False`` if not found.
        """
        stmt = select(MediaSpeciesTag).where(
            MediaSpeciesTag.media_id == media_id,
            MediaSpeciesTag.species_id == species_id,
        )
        result = await self.session.execute(stmt)
        tag = result.scalar_one_or_none()
        if tag is None:
            return False
        await self.session.delete(tag)
        await self.session.flush()
        return True

    async def delete_tags_for_media(self, media_id: uuid.UUID) -> int:
        """Delete all species tags for a media item.

        Args:
            media_id: The media UUID.

        Returns:
            The number of tags deleted.
        """
        stmt = select(MediaSpeciesTag).where(MediaSpeciesTag.media_id == media_id)
        result = await self.session.execute(stmt)
        tags = result.scalars().all()
        count = len(tags)
        for tag in tags:
            await self.session.delete(tag)
        if count:
            await self.session.flush()
        return count
