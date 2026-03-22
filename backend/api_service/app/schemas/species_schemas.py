"""Pydantic schemas for the species catalog API endpoints."""

from datetime import datetime as DateTime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class SpeciesCatalogResponse(BaseModel):
    """Full species entry returned from the catalog endpoint."""

    id: UUID
    ml_label: str
    scientific_name: str
    common_name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    habitat: Optional[Any] = None
    locations: Optional[Any] = None
    taxonomy: Optional[Any] = None
    image_urls: Optional[Any] = None
    created_at: DateTime
    updated_at: DateTime

    model_config = {"from_attributes": True}


class SpeciesListResponse(BaseModel):
    """Paginated response for the species catalog list endpoint."""

    items: list[SpeciesCatalogResponse]
    total: int
    limit: int
    offset: int
