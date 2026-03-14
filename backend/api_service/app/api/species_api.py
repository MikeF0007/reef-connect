"""FastAPI router for the species catalog endpoint."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.database import get_db_session
from common.db.repositories.species_repository import SpeciesRepository

from ..schemas.species_schemas import SpeciesListResponse
from ..services.species_service import SpeciesService


def get_species_service(
    session: AsyncSession = Depends(get_db_session),
) -> SpeciesService:
    """Dependency to get SpeciesService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        SpeciesService: An instance of SpeciesService.
    """
    return SpeciesService(species_repo=SpeciesRepository(session))


router = APIRouter(prefix="/api/species", tags=["species"])


@router.get("", response_model=SpeciesListResponse)
async def list_species(
    search: Optional[str] = Query(None, description="Search by name or ML label"),
    category: Optional[str] = Query(None, description="Filter by taxonomy category"),
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0),
    service: SpeciesService = Depends(get_species_service),
) -> SpeciesListResponse:
    """Get a paginated list of species from the catalog.

    Supports optional free-text search across common name, scientific name,
    and ML label, as well as taxonomy category filtering.  ``search`` takes
    precedence over ``category`` when both are supplied.

    Args:
        search: Optional search string matched against species names and ML label.
        category: Optional taxonomy category substring filter.
        limit: Maximum number of results (1–100, default 20).
        offset: Number of results to skip (default 0).
        service: Species service instance.

    Returns:
        SpeciesListResponse: Paginated list of species with total count.
    """
    return await service.list_species(
        search=search,
        category=category,
        limit=limit,
        offset=offset,
    )
