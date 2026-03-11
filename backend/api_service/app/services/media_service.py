"""Service layer for media and species tagging operations."""

import uuid
from typing import Optional
from uuid import UUID

from common.db.models.core_models import Media
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.species_repository import SpeciesRepository
from common.db.repositories.species_tag_repository import SpeciesTagRepository
from common.types.enums import MediaType, SpeciesTagSource

from ..schemas.media_schemas import (
    AddTagRequest,
    MediaDeleteResponse,
    MediaResponse,
    MediaUpdate,
    MediaUploadResponse,
    MediaWithTagsResponse,
    SpeciesResponse,
    SpeciesTagResponse,
    TagWithSpeciesResponse,
)

_ACCEPTED_MIME_PREFIXES = ("image/", "video/")


def _infer_media_type(mime_type: str) -> Optional[MediaType]:
    """Infer MediaType enum value from a MIME type string.

    Args:
        mime_type: The MIME type string (e.g. ``"image/jpeg"``).

    Returns:
        ``MediaType.IMAGE`` or ``MediaType.VIDEO``, or ``None`` if unrecognised.
    """
    if mime_type.startswith("image/"):
        return MediaType.IMAGE
    if mime_type.startswith("video/"):
        return MediaType.VIDEO
    return None


class MediaService:
    """Service for media upload, retrieval, update, deletion, and species tagging.

    Attributes:
        media_repo: Repository handling Media CRUD and tag reads.
        species_repo: Repository handling species lookups.
        species_tag_repo: Repository handling species tag CRUD.
    """

    def __init__(
        self,
        media_repo: MediaRepository,
        species_repo: SpeciesRepository,
        species_tag_repo: SpeciesTagRepository,
    ) -> None:
        """Initialise the MediaService with its required repositories.

        Args:
            media_repo: Repository for media operations.
            species_repo: Repository for species lookups.
            species_tag_repo: Repository for species tag operations.
        """
        self.media_repo = media_repo
        self.species_repo = species_repo
        self.species_tag_repo = species_tag_repo

    # ---- Helpers ----

    async def _build_media_with_tags(self, media: Media) -> MediaWithTagsResponse:
        """Build a MediaWithTagsResponse from a Media instance.

        Fetches associated species tags and resolves the species data for each
        tag in a single batch query.

        Args:
            media: The Media ORM instance.

        Returns:
            MediaWithTagsResponse with populated tags and species.
        """
        tags = await self.media_repo.get_species_tags_for_media(media.id)
        species_ids = [tag.species_id for tag in tags]
        if species_ids:
            species_list = await self.species_repo.get_species_by_ids(species_ids)
            species_map = {s.id: s for s in species_list}
        else:
            species_map = {}

        tag_responses: list[TagWithSpeciesResponse] = []
        for tag in tags:
            species = species_map.get(tag.species_id)
            if species:
                tag_responses.append(
                    TagWithSpeciesResponse(
                        tag=SpeciesTagResponse.model_validate(tag),
                        species=SpeciesResponse.model_validate(species),
                    )
                )

        return MediaWithTagsResponse(
            media=MediaResponse.model_validate(media),
            tags=tag_responses,
        )

    # ---- Media CRUD ----

    async def upload_media(
        self,
        *,
        user_id: UUID,
        dive_log_id: UUID,
        filename: str,
        mime_type: str,
        file_size_bytes: int,
        description: Optional[str] = None,
    ) -> MediaUploadResponse:
        """Register a new media upload and create the database record.

        The storage_key is generated as a placeholder path. Actual file
        transfer to blob storage is handled outside this service (e.g. by
        the media worker after the record is created with PENDING status).

        Args:
            user_id: ID of the uploading user.
            dive_log_id: ID of the dive log the media is associated with.
            filename: Original filename of the uploaded file.
            mime_type: MIME type declared by the client (e.g. ``"image/jpeg"``).
            file_size_bytes: Size of the uploaded file in bytes.
            description: Optional caption / description.

        Returns:
            MediaUploadResponse with the created Media and an upload_status of
            ``"accepted"`` for supported MIME types, ``"rejected"`` otherwise.
        """
        media_type = _infer_media_type(mime_type)
        if media_type is None:
            # Build a minimal rejected response without persisting anything
            storage_key = f"media/{user_id}/{uuid.uuid4()}/{filename}"
            media_id = await self.media_repo.create_media(
                user_id=user_id,
                storage_key=storage_key,
                type=MediaType.IMAGE,  # placeholder — won't be processed
                dive_log_id=dive_log_id,
                mime_type=mime_type,
                file_size_bytes=file_size_bytes,
                description=description,
            )
            media = await self.media_repo.get_media_by_id(media_id)
            return MediaUploadResponse(
                media=MediaResponse.model_validate(media),
                upload_status="rejected",
            )

        storage_key = f"media/{user_id}/{uuid.uuid4()}/{filename}"
        media_id = await self.media_repo.create_media(
            user_id=user_id,
            storage_key=storage_key,
            type=media_type,
            dive_log_id=dive_log_id,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            description=description,
        )
        media = await self.media_repo.get_media_by_id(media_id)
        return MediaUploadResponse(
            media=MediaResponse.model_validate(media),
            upload_status="accepted",
        )

    async def get_media_list(
        self,
        *,
        user_id: Optional[UUID] = None,
        dive_log_id: Optional[UUID] = None,
        media_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MediaWithTagsResponse]:
        """Retrieve media with their species tags.

        Either ``user_id`` or ``dive_log_id`` must be provided. When
        ``dive_log_id`` is supplied it takes precedence over ``user_id``.

        Args:
            user_id: Filter by owning user.
            dive_log_id: Filter by associated dive log.
            media_type: Optional MediaType filter string.
            limit: Maximum number of results (1–100).
            offset: Number of results to skip.

        Returns:
            List of MediaWithTagsResponse objects, each containing the media
            item and its resolved species tags.

        Raises:
            ValueError: If neither ``user_id`` nor ``dive_log_id`` is provided.
        """
        if dive_log_id is not None:
            media_list = await self.media_repo.get_media_by_dive_log(
                dive_log_id, media_type=media_type
            )
            # Apply manual pagination since repository method doesn't support it
            media_list = media_list[offset : offset + limit]
        elif user_id is not None:
            media_list = await self.media_repo.get_media_by_user(
                user_id, media_type=media_type, limit=limit, offset=offset
            )
        else:
            raise ValueError("Either user_id or dive_log_id must be provided")

        return [await self._build_media_with_tags(m) for m in media_list]

    async def update_media(
        self, media_id: UUID, user_id: UUID, data: MediaUpdate
    ) -> MediaResponse:
        """Update media metadata if the media belongs to the requesting user.

        Args:
            media_id: UUID of the media to update.
            user_id: UUID of the requesting user (for ownership check).
            data: Fields to update.

        Returns:
            MediaResponse with updated data.

        Raises:
            ValueError: If the media does not exist or belongs to another user.
        """
        media = await self.media_repo.get_media_by_id(media_id)
        if not media or media.user_id != user_id:
            raise ValueError("Media not found or access denied")
        await self.media_repo.update_media_details(
            media_id, data.model_dump(exclude_unset=True)
        )
        updated = await self.media_repo.get_media_by_id(media_id)
        return MediaResponse.model_validate(updated)

    async def delete_media(self, media_id: UUID, user_id: UUID) -> MediaDeleteResponse:
        """Delete a media item and all its species tags if it belongs to the user.

        Args:
            media_id: UUID of the media to delete.
            user_id: UUID of the requesting user (for ownership check).

        Returns:
            MediaDeleteResponse with success flag and tag count removed.

        Raises:
            ValueError: If the media does not exist or belongs to another user.
        """
        media = await self.media_repo.get_media_by_id(media_id)
        if not media or media.user_id != user_id:
            raise ValueError("Media not found or access denied")

        tags = await self.media_repo.get_species_tags_for_media(media_id)
        removed_tags_count = len(tags)

        await self.media_repo.delete_media(media_id)
        return MediaDeleteResponse(success=True, removed_tags_count=removed_tags_count)

    # ---- Species Tagging ----

    async def add_tag(
        self, media_id: UUID, user_id: UUID, data: AddTagRequest
    ) -> TagWithSpeciesResponse:
        """Add a user-sourced species tag to a media item.

        Args:
            media_id: UUID of the media to tag.
            user_id: UUID of the requesting user (for ownership check).
            data: AddTagRequest containing the species_id to tag.

        Returns:
            TagWithSpeciesResponse with the new tag and species data.

        Raises:
            ValueError: If the media is not found, belongs to another user,
                the species is not found, or the tag already exists.
        """
        media = await self.media_repo.get_media_by_id(media_id)
        if not media or media.user_id != user_id:
            raise ValueError("Media not found or access denied")

        species = await self.species_repo.get_species_by_id(data.species_id)
        if not species:
            raise ValueError("Species not found")

        already_exists = await self.species_tag_repo.check_tag_exists(
            media_id, data.species_id
        )
        if already_exists:
            raise ValueError("Tag already exists for this media and species")

        tag = await self.species_tag_repo.create_tag(
            media_id=media_id,
            species_id=data.species_id,
            source=SpeciesTagSource.USER,
        )
        return TagWithSpeciesResponse(
            tag=SpeciesTagResponse.model_validate(tag),
            species=SpeciesResponse.model_validate(species),
        )

    async def delete_tag(self, media_id: UUID, user_id: UUID, tag_id: UUID) -> bool:
        """Remove a species tag from a media item.

        Args:
            media_id: UUID of the media item.
            user_id: UUID of the requesting user (for ownership check).
            tag_id: UUID of the species (acts as the tag identifier since the
                composite PK is ``(media_id, species_id)``).

        Returns:
            ``True`` if the tag was deleted, ``False`` if it was not found.

        Raises:
            ValueError: If the media is not found or belongs to another user.
        """
        media = await self.media_repo.get_media_by_id(media_id)
        if not media or media.user_id != user_id:
            raise ValueError("Media not found or access denied")

        return await self.species_tag_repo.delete_tag(media_id, tag_id)
