"""Service layer for species catalog operations."""

from typing import Optional

from common.db.repositories.species_repository import SpeciesRepository

from ..schemas.species_schemas import SpeciesCatalogResponse, SpeciesListResponse


class SpeciesService:
    """Service for reading from the species catalog.

    Attributes:
        species_repo: Repository for species lookups and searches.
    """

    def __init__(self, species_repo: SpeciesRepository) -> None:
        self.species_repo = species_repo

    async def list_species(
        self,
        search: Optional[str],
        category: Optional[str],
        limit: int,
        offset: int,
    ) -> SpeciesListResponse:
        """Return a paginated, optionally filtered list of species.

        When ``search`` is provided it takes precedence over ``category``.
        When both are omitted all species are returned ordered alphabetically
        by common name.

        Args:
            search: Free-text search against common name, scientific name,
                and ML label.
            category: Taxonomy category substring filter.
            limit: Maximum number of items to return (1–100).
            offset: Number of items to skip.

        Returns:
            SpeciesListResponse with items and pagination metadata.
        """
        if search:
            species = await self.species_repo.search_species(
                query=search, limit=limit, offset=offset
            )
        elif category:
            species = await self.species_repo.get_species_by_category(
                category=category, limit=limit, offset=offset
            )
        else:
            species = await self.species_repo.get_all_species(
                limit=limit, offset=offset
            )

        total = await self.species_repo.get_species_count()

        return SpeciesListResponse(
            items=[SpeciesCatalogResponse.model_validate(s) for s in species],
            total=total,
            limit=limit,
            offset=offset,
        )
