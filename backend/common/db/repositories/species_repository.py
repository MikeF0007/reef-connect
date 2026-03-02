"""DB-based ISpeciesRepository implementation.

Provides async read and search operations for the species catalog.
"""

import uuid
from typing import Optional

from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import Species
from common.db.repositories.interfaces import ISpeciesRepository


class SpeciesRepository(ISpeciesRepository):
    """Provides async read and search operations over the species catalog.

    The species catalog is a reference dataset; all methods are read-only
    — no insert, update, or delete operations are exposed.

    Attributes:
        session: AsyncSession used for all DB operations, ensuring
            transaction consistency across method calls.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ================ Species Lookups ================

    async def get_species_by_id(self, species_id: uuid.UUID) -> Optional[Species]:
        """Retrieve a single species by its UUID.

        Args:
            species_id: The UUID of the species to retrieve.

        Returns:
            The matching Species instance, or ``None`` if not found.
        """
        stmt = select(Species).where(Species.id == species_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_species_by_ids(self, species_ids: list[uuid.UUID]) -> list[Species]:
        """Retrieve multiple species by their UUIDs in a single query.

        Args:
            species_ids: UUIDs of the species to retrieve.

        Returns:
            A list of found Species instances (missing IDs are silently skipped).
        """
        if not species_ids:
            return []
        stmt = select(Species).where(Species.id.in_(species_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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
        stmt = select(Species).order_by(Species.common_name)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_species_by_category(
        self,
        category: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Species]:
        """Retrieve species filtered by taxonomy category.

        Performs a case-insensitive substring match against the serialized
        ``taxonomy`` JSON field.  Results are ordered alphabetically by
        ``common_name``.

        Args:
            category: Category string to search for within the taxonomy field.
            limit: Maximum number of results to return.
            offset: Number of results to skip before returning.

        Returns:
            A list of matching Species instances.
        """
        stmt = (
            select(Species)
            .where(cast(Species.taxonomy, Text).ilike(f"%{category}%"))
            .order_by(Species.common_name)
        )
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_species_by_ml_label(self, ml_label: str) -> Optional[Species]:
        """Retrieve a species by its ML label identifier.

        Args:
            ml_label: The unique ML label string.

        Returns:
            The matching Species instance, or ``None`` if not found.
        """
        stmt = select(Species).where(Species.ml_label == ml_label)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_species_by_slug(self, slug: str) -> Optional[Species]:
        """Retrieve a species by its URL-friendly slug.

        Args:
            slug: The unique slug string.

        Returns:
            The matching Species instance, or ``None`` if not found.
        """
        stmt = select(Species).where(Species.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_species_count(self) -> int:
        """Return the total number of species in the catalog.

        Returns:
            Integer count of all rows in the ``species`` table.
        """
        stmt = select(func.count()).select_from(Species)
        result = await self.session.execute(stmt)
        return result.scalar_one()

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
        pattern = f"%{query}%"
        stmt = (
            select(Species)
            .where(
                or_(
                    Species.common_name.ilike(pattern),
                    Species.scientific_name.ilike(pattern),
                    Species.ml_label.ilike(pattern),
                )
            )
            .order_by(Species.common_name)
        )
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
