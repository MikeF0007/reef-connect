"""FastAPI router for media and species tagging endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.database import get_db_session
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.species_repository import SpeciesRepository
from common.db.repositories.species_tag_repository import SpeciesTagRepository

from ..schemas.media_schemas import (
    AddTagRequest,
    DeleteTagResponse,
    MediaDeleteResponse,
    MediaResponse,
    MediaUpdate,
    MediaUploadResponse,
    MediaWithTagsResponse,
    TagWithSpeciesResponse,
)
from ..services.media_service import MediaService
from .auth_api import get_current_user_id  # noqa: F401  (re-exported for dependency override)


def get_media_service(
    session: AsyncSession = Depends(get_db_session),
) -> MediaService:
    """Dependency to get MediaService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        MediaService: An instance of MediaService.
    """
    return MediaService(
        media_repo=MediaRepository(session),
        species_repo=SpeciesRepository(session),
        species_tag_repo=SpeciesTagRepository(session),
    )


router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("", response_model=List[MediaWithTagsResponse])
async def get_media(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    dive_log_id: Optional[UUID] = Query(None, description="Filter by dive log ID"),
    media_type: Optional[str] = Query(
        None, description="Filter by media type ('image' or 'video')"
    ),
    limit: Optional[int] = Query(20, gt=0, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user_id: UUID = Depends(get_current_user_id),
    service: MediaService = Depends(get_media_service),
) -> List[MediaWithTagsResponse]:
    """Get media items with their species tags.

    Returns media for a specific user or dive log. When neither ``user_id``
    nor ``dive_log_id`` is provided the current user's media is returned.

    Args:
        user_id: Optional user ID to filter by (defaults to current user).
        dive_log_id: Optional dive log ID to filter by (takes precedence
            over user_id).
        media_type: Optional media type filter.
        limit: Maximum number of results.
        offset: Number of results to skip.
        current_user_id: Current authenticated user ID.
        service: Media service instance.

    Returns:
        List[MediaWithTagsResponse]: Media items with associated species tags.
    """
    target_user_id = user_id if user_id is not None else current_user_id
    try:
        return await service.get_media_list(
            user_id=target_user_id if dive_log_id is None else None,
            dive_log_id=dive_log_id,
            media_type=media_type,
            limit=limit,
            offset=offset,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", response_model=MediaUploadResponse, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    dive_log_id: UUID = Form(...),
    caption: Optional[str] = Form(None),
    current_user_id: UUID = Depends(get_current_user_id),
    service: MediaService = Depends(get_media_service),
) -> MediaUploadResponse:
    """Upload a media file and associate it with a dive log.

    Stores file metadata and creates a PENDING media record. The actual
    file transfer to blob storage is handled asynchronously by the media
    worker after this endpoint returns.

    Args:
        file: The file to upload.
        dive_log_id: ID of the dive log to associate the media with.
        caption: Optional description / caption for the media.
        current_user_id: Current authenticated user ID.
        service: Media service instance.

    Returns:
        MediaUploadResponse: The created media record and upload status.
    """
    content = await file.read()
    file_size_bytes = len(content)
    mime_type = file.content_type or "application/octet-stream"
    filename = file.filename or "upload"

    return await service.upload_media(
        user_id=current_user_id,
        dive_log_id=dive_log_id,
        filename=filename,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        description=caption,
    )


@router.patch("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: UUID,
    data: MediaUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    service: MediaService = Depends(get_media_service),
) -> MediaResponse:
    """Update media description.

    Args:
        media_id: UUID of the media item to update.
        data: Fields to update (currently only description).
        current_user_id: Current authenticated user ID.
        service: Media service instance.

    Returns:
        MediaResponse: The updated media item.
    """
    try:
        return await service.update_media(media_id, current_user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{media_id}", response_model=MediaDeleteResponse)
async def delete_media(
    media_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    service: MediaService = Depends(get_media_service),
) -> MediaDeleteResponse:
    """Delete a media item and all its associated species tags.

    Args:
        media_id: UUID of the media item to delete.
        current_user_id: Current authenticated user ID.
        service: Media service instance.

    Returns:
        MediaDeleteResponse: Success flag and count of removed tags.
    """
    try:
        return await service.delete_media(media_id, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{media_id}/tags", response_model=TagWithSpeciesResponse, status_code=201)
async def add_tag(
    media_id: UUID,
    data: AddTagRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    service: MediaService = Depends(get_media_service),
) -> TagWithSpeciesResponse:
    """Tag a species on a media item.

    Args:
        media_id: UUID of the media item to tag.
        data: AddTagRequest with the species_id to tag.
        current_user_id: Current authenticated user ID.
        service: Media service instance.

    Returns:
        TagWithSpeciesResponse: The new tag and associated species data.
    """
    try:
        return await service.add_tag(media_id, current_user_id, data)
    except ValueError as e:
        status_code = 409 if "already exists" in str(e) else 404
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete("/{media_id}/tags/{tag_id}", response_model=DeleteTagResponse)
async def delete_tag(
    media_id: UUID,
    tag_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    service: MediaService = Depends(get_media_service),
) -> DeleteTagResponse:
    """Remove a species tag from a media item.

    The ``tag_id`` path parameter is the species UUID (since the composite
    primary key of a tag is ``(media_id, species_id)``).

    Args:
        media_id: UUID of the media item.
        tag_id: UUID of the species whose tag should be removed.
        current_user_id: Current authenticated user ID.
        service: Media service instance.

    Returns:
        DeleteTagResponse: Success flag indicating whether the tag was removed.
    """
    try:
        deleted = await service.delete_tag(media_id, current_user_id, tag_id)
        return DeleteTagResponse(success=deleted)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
