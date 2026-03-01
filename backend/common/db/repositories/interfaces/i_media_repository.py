"""Interface for the media repository."""

import uuid
from typing import Optional, Protocol

from common.db.models.core_models import Media, MediaSpeciesTag


class IMediaRepository(Protocol):
    """Protocol defining the contract for media CRUD operations."""

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
        ...

    async def get_media_by_id(self, media_id: uuid.UUID) -> Optional[Media]:
        """Retrieve a single media item by its ID.

        Args:
            media_id: The media UUID.

        Returns:
            The Media if found, otherwise ``None``.
        """
        ...

    async def get_media_by_ids(self, media_ids: list[uuid.UUID]) -> list[Media]:
        """Retrieve media items by their IDs in a single query.

        Args:
            media_ids: List of media UUIDs to look up.

        Returns:
            A list of found Media instances (missing IDs are silently skipped).
        """
        ...

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
        ...

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
        ...

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

        Returns media owned by *user_id* that have been tagged with *species_id*,
        ordered by ``created_at`` descending.

        Args:
            user_id: The user UUID (results are scoped to this user's media).
            species_id: The species UUID to filter by.
            media_type: Optional filter by media type (see ``MediaType`` enum).
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            A paginated list of matching Media instances.
        """
        ...

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
        ...

    async def update_media_status(self, media_id: uuid.UUID, status: str) -> None:
        """Update the processing status of a media item.

        Args:
            media_id: The UUID of the media item to update.
            status: New status value (see ``MediaStatus`` enum,
                e.g. ``"PENDING"``, ``"UPLOADING"``, ``"PROCESSED"``).
        """
        ...

    async def update_media_details(self, media_id: uuid.UUID, details: dict) -> None:
        """Update specific fields of a media item.

        Only fields present in *details* are modified. Set a value to
        ``None`` to clear an optional field.

        Args:
            media_id: The UUID of the media item to update.
            details: Field-name → new-value mapping. Supported fields include
                description, dive_log_id, mime_type, file_size_bytes,
                width, height, duration_seconds, taken_at, media_visibility, etc.
        """
        ...

    async def delete_media(self, media_id: uuid.UUID) -> bool:
        """Delete a media item by its ID along with its species tags.

        Species tags are cascade-deleted automatically via the
        ``all, delete-orphan`` relationship on ``Media.species_tags``.

        Args:
            media_id: The UUID of the media item to delete.

        Returns:
            ``True`` if the media was deleted, ``False`` if not found.
        """
        ...
