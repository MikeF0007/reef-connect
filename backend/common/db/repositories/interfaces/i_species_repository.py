"""Interface for the species repository."""

import uuid
from typing import Optional, Protocol

from common.db.models.core_models import Species


class ISpeciesRepository(Protocol):
    """Protocol defining the contract for species catalog read and search operations.

    The species catalog is a read-only reference dataset seeded from ML labels.
    All methods are non-mutating lookups and searches over the ``species`` table.
    """

    async def get_species_by_id(self, species_id: uuid.UUID) -> Optional[Species]:
        """Retrieve a single species by its UUID.

        Args:
            species_id: The UUID of the species to retrieve.

        Returns:
            The matching Species instance, or ``None`` if not found.
        """
        ...

    async def get_species_by_ids(self, species_ids: list[uuid.UUID]) -> list[Species]:
        """Retrieve multiple species by their UUIDs in a single query.

        Missing IDs are silently skipped — the returned list may be shorter
        than *species_ids*.

        Args:
            species_ids: UUIDs of the species to retrieve.

        Returns:
            A list of found Species instances.
        """
        ...

    async def get_all_species(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Species]:
        """Retrieve all species in the catalog with optional pagination.

        Results are ordered alphabetically by ``common_name``.

        Args:
            limit: Maximum number of results to return.
            offset: Number of results to skip before returning.

        Returns:
            A paginated list of Species instances.
        """
        ...

    async def get_species_by_category(
        self,
        category: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Species]:
        """Retrieve species filtered by taxonomy category.

        Performs a case-insensitive substring match against the serialized
        ``taxonomy`` JSON field (e.g. ``"fish"``, ``"coral"``, ``"mammal"``).
        Results are ordered alphabetically by ``common_name``.

        Args:
            category: Category string to search for within the taxonomy field.
            limit: Maximum number of results to return.
            offset: Number of results to skip before returning.

        Returns:
            A list of matching Species instances.
        """
        ...

    async def get_species_by_ml_label(self, ml_label: str) -> Optional[Species]:
        """Retrieve a species by its ML label identifier.

        Args:
            ml_label: The unique ML label string (e.g. ``"acanthurus_lineatus"``).

        Returns:
            The matching Species instance, or ``None`` if not found.
        """
        ...

    async def get_species_by_slug(self, slug: str) -> Optional[Species]:
        """Retrieve a species by its URL-friendly slug.

        Args:
            slug: The unique slug string (e.g. ``"lined-surgeonfish"``).

        Returns:
            The matching Species instance, or ``None`` if not found.
        """
        ...

    async def get_species_count(self) -> int:
        """Return the total number of species in the catalog.

        Returns:
            Integer count of all rows in the ``species`` table.
        """
        ...

    async def search_species(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Species]:
        """Search for species by common name, scientific name, or ML label.

        Performs a case-insensitive partial match against ``common_name``,
        ``scientific_name``, and ``ml_label``.  Results are ordered
        alphabetically by ``common_name``.

        Args:
            query: Partial search string to match against species names.
            limit: Maximum number of results to return.
            offset: Number of results to skip before returning.

        Returns:
            A paginated list of matching Species instances.
        """
        ...
