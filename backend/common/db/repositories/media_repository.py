"""DB-based IMediaRepository implementation.

Provides async CRUD operations for media entries and their species tags.
"""

import uuid
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import Media, MediaSpeciesTag
from common.db.repositories.interfaces import IMediaRepository
from common.types import MediaStatus


class MediaRepository(IMediaRepository):
    """Provides async CRUD operations for Media entries.

    Attributes:
        session: AsyncSession used for all DB operations, ensuring
            transaction consistency across method calls.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ================ Helpers ================

    def _apply_pagination(self, stmt, limit: Optional[int], offset: Optional[int]):
        """Apply optional OFFSET / LIMIT clauses to a statement.

        Args:
            stmt: The current select statement.
            limit: Maximum number of rows. Skipped when ``None``.
            offset: Number of rows to skip. Skipped when ``None``.

        Returns:
            The modified statement.
        """
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return stmt

    # ================ Media CRUD ================

    async def create_media(
        self,
        *,
        user_id: uuid.UUID,
        storage_key: str,
        type: str,
        **kwargs: object,
    ) -> uuid.UUID:
        """Create a new media entry and return its ID.

        The initial status is set to ``PENDING`` automatically.

        Args:
            user_id: ID of the owning user.
            storage_key: Blob storage key for the media file.
            type: Media type (see ``MediaType`` enum).
            **kwargs: Optional model fields
                (dive_log_id, mime_type, file_size_bytes, description, etc.).

        Returns:
            The UUID of the newly created media entry.

        Raises:
            sqlalchemy.exc.IntegrityError: If *user_id* does not
                reference an existing user.
        """
        media = Media(
            user_id=user_id,
            storage_key=storage_key,
            type=type,
            status=MediaStatus.PENDING,
            **kwargs,
        )
        self.session.add(media)
        await self.session.flush()
        return media.id

    async def get_media_by_id(self, media_id: uuid.UUID) -> Optional[Media]:
        """Retrieve a single media item by its ID.

        Args:
            media_id: The media UUID.

        Returns:
            The Media if found, otherwise ``None``.
        """
        stmt = select(Media).where(Media.id == media_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_media_by_ids(self, media_ids: list[uuid.UUID]) -> list[Media]:
        """Retrieve media items by their IDs in a single query.

        Args:
            media_ids: UUIDs to look up.

        Returns:
            A list of found Media instances (missing IDs are silently skipped).
        """
        if not media_ids:
            return []
        stmt = select(Media).where(Media.id.in_(media_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_media_by_user(
        self,
        user_id: uuid.UUID,
        *,
        media_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Media]:
        """Retrieve media items for a user with optional type filter and pagination.

        Results are ordered by ``created_at`` descending (newest first).

        Args:
            user_id: The user UUID.
            media_type: Optional filter by media type (see ``MediaType`` enum).
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            A paginated list of Media instances belonging to the user.
        """
        stmt = (
            select(Media)
            .where(Media.user_id == user_id)
            .order_by(desc(Media.created_at))
        )
        if media_type is not None:
            stmt = stmt.where(Media.type == media_type)
        stmt = self._apply_pagination(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_media_by_dive_log(
        self,
        dive_log_id: uuid.UUID,
        *,
        media_type: Optional[str] = None,
    ) -> list[Media]:
        """Retrieve media items associated with a specific dive log.

        Results are ordered by ``created_at`` descending (newest first).

        Args:
            dive_log_id: The dive log UUID.
            media_type: Optional filter by media type (see ``MediaType`` enum).

        Returns:
            A list of Media instances linked to the given dive log.
        """
        stmt = (
            select(Media)
            .where(Media.dive_log_id == dive_log_id)
            .order_by(desc(Media.created_at))
        )
        if media_type is not None:
            stmt = stmt.where(Media.type == media_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_media_by_species_tag(
        self,
        user_id: uuid.UUID,
        species_id: uuid.UUID,
        *,
        media_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Media]:
        """Retrieve a user's media items filtered by species tag.

        Args:
            user_id: The user UUID (results are scoped to this user's media).
            species_id: The species UUID to filter by.
            media_type: Optional filter by media type (see ``MediaType`` enum).
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            A paginated list of matching Media instances.
        """
        stmt = (
            select(Media)
            .join(MediaSpeciesTag, MediaSpeciesTag.media_id == Media.id)
            .where(
                Media.user_id == user_id,
                MediaSpeciesTag.species_id == species_id,
            )
            .order_by(desc(Media.created_at))
        )
        if media_type is not None:
            stmt = stmt.where(Media.type == media_type)
        stmt = self._apply_pagination(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_species_tags_for_media(
        self, media_id: uuid.UUID
    ) -> list[MediaSpeciesTag]:
        """Retrieve all species tags associated with a media item.

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

    async def update_media_status(self, media_id: uuid.UUID, status: str) -> None:
        """Update the processing status of a media item.

        Args:
            media_id: The UUID of the media item to update.
            status: New status value (see ``MediaStatus`` enum).
        """
        media = await self.get_media_by_id(media_id)
        if media is None:
            return
        media.status = status
        self.session.add(media)
        await self.session.flush()

    async def update_media_details(self, media_id: uuid.UUID, details: dict) -> None:
        """Update specific fields of a media item.

        Only fields present in *details* are modified. Set a value to
        ``None`` to clear an optional field.

        Args:
            media_id: The UUID of the media item to update.
            details: Field-name → new-value mapping.
        """
        media = await self.get_media_by_id(media_id)
        if media is None:
            return
        for key, value in details.items():
            if hasattr(media, key):
                setattr(media, key, value)
        self.session.add(media)
        await self.session.flush()

    async def delete_media(self, media_id: uuid.UUID) -> bool:
        """Delete a media item by its ID along with its species tags.

        Species tags are cascade-deleted automatically via the
        ``all, delete-orphan`` relationship on ``Media.species_tags``.

        Args:
            media_id: The UUID of the media item to delete.

        Returns:
            ``True`` if the media was deleted, ``False`` if not found.
        """
        media = await self.get_media_by_id(media_id)
        if media is None:
            return False
        await self.session.delete(media)
        await self.session.flush()
        return True
