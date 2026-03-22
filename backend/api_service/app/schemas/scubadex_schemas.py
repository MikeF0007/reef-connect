"""Pydantic schemas for the ScubaDex API endpoint."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .media_schemas import MediaResponse
from .species_schemas import SpeciesCatalogResponse


class ScubaDexEntryResponse(BaseModel):
    """A single entry in a user's ScubaDex."""

    species: SpeciesCatalogResponse
    first_seen_date: date
    encounter_count: int
    sample_media: Optional[list[MediaResponse]] = None


class ScubaDexResponse(BaseModel):
    """Full ScubaDex response for a user."""

    entries: list[ScubaDexEntryResponse]
    total_discovered: int
    total_species: int
    percent_complete: float
