"""Pydantic schemas for media and species tagging API endpoints."""

from datetime import datetime as DateTime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from common.types.enums import MediaStatus, MediaType, SpeciesTagSource, Visibility


class MediaResponse(BaseModel):
    """Response schema for a media item."""

    id: UUID
    user_id: UUID
    status: MediaStatus
    type: MediaType
    dive_log_id: Optional[UUID] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    description: Optional[str] = None
    media_visibility: Optional[Visibility] = None
    ml_tagging_status: Optional[str] = None
    created_at: DateTime
    updated_at: DateTime

    model_config = {"from_attributes": True}


class SpeciesResponse(BaseModel):
    """Minimal species schema used within tag responses."""

    id: UUID
    ml_label: str
    scientific_name: str
    common_name: str
    slug: Optional[str] = None

    model_config = {"from_attributes": True}


class SpeciesTagResponse(BaseModel):
    """Response schema for a species tag on a media item."""

    media_id: UUID
    species_id: UUID
    source: SpeciesTagSource
    tagged_at: DateTime

    model_config = {"from_attributes": True}


class TagWithSpeciesResponse(BaseModel):
    """Combined tag and species data for a single tag entry."""

    tag: SpeciesTagResponse
    species: SpeciesResponse


class MediaWithTagsResponse(BaseModel):
    """Media item with its associated species tags and species data."""

    media: MediaResponse
    tags: list[TagWithSpeciesResponse]


class MediaUploadResponse(BaseModel):
    """Response for a media upload request."""

    media: MediaResponse
    upload_status: str  # "accepted" | "rejected"


class MediaDeleteResponse(BaseModel):
    """Response for a media deletion request."""

    success: bool
    removed_tags_count: int


class MediaUpdate(BaseModel):
    """Schema for updating media metadata."""

    description: Optional[str] = None


class AddTagRequest(BaseModel):
    """Request schema for adding a species tag to a media item."""

    species_id: UUID


class DeleteTagResponse(BaseModel):
    """Response for a tag deletion request."""

    success: bool
