"""Unit tests for SpeciesRepository.

Tests cover all read and search operations against an in-memory SQLite database.
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import Species
from common.db.repositories.species_repository import SpeciesRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_test_species(session: AsyncSession, **overrides: Any) -> Species:
    """Insert a species with sensible defaults and return the instance.

    Args:
        session: AsyncSession to use for DB operations.
        overrides: Field values to override the defaults.

    Returns:
        The created Species instance.
    """
    defaults: dict[str, Any] = {
        "ml_label": f"species_{uuid.uuid4().hex[:8]}",
        "scientific_name": "Testus speciesus",
        "common_name": "Test Fish",
    }
    defaults.update(overrides)
    species = Species(**defaults)
    session.add(species)
    await session.flush()
    return species


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSpeciesRepository:
    """Tests for SpeciesRepository covering all read and search operations."""

    # ============================================================================
    # Get By ID Tests
    # ============================================================================

    async def test_get_species_by_id_returns_correct_species(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_id returns the species with the given UUID.

        Args:
            async_session: Database session for the test.
        """
        species = await _create_test_species(async_session)

        result = await SpeciesRepository(async_session).get_species_by_id(species.id)

        assert result is not None
        assert result.id == species.id

    async def test_get_species_by_id_returns_none_when_not_found(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_id returns None for a non-existent UUID.

        Args:
            async_session: Database session for the test.
        """
        result = await SpeciesRepository(async_session).get_species_by_id(uuid.uuid4())

        assert result is None

    async def test_get_species_by_id_persists_all_fields(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_id returns a species with all provided fields intact.

        Args:
            async_session: Database session for the test.
        """
        species = await _create_test_species(
            async_session,
            ml_label="acanthurus_lineatus",
            scientific_name="Acanthurus lineatus",
            common_name="Lined Surgeonfish",
            slug="lined-surgeonfish",
        )

        result = await SpeciesRepository(async_session).get_species_by_id(species.id)

        assert result is not None
        assert result.ml_label == "acanthurus_lineatus"
        assert result.scientific_name == "Acanthurus lineatus"
        assert result.common_name == "Lined Surgeonfish"
        assert result.slug == "lined-surgeonfish"

    # ============================================================================
    # Get By IDs Tests
    # ============================================================================

    async def test_get_species_by_ids_returns_all_matching(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_ids returns all species for the given UUIDs.

        Args:
            async_session: Database session for the test.
        """
        species_a = await _create_test_species(async_session)
        species_b = await _create_test_species(async_session)

        results = await SpeciesRepository(async_session).get_species_by_ids(
            [species_a.id, species_b.id]
        )

        assert len(results) == 2
        returned_ids = {s.id for s in results}
        assert returned_ids == {species_a.id, species_b.id}

    async def test_get_species_by_ids_skips_missing_ids(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_ids silently omits non-existent UUIDs.

        Args:
            async_session: Database session for the test.
        """
        species = await _create_test_species(async_session)

        results = await SpeciesRepository(async_session).get_species_by_ids(
            [species.id, uuid.uuid4()]
        )

        assert len(results) == 1
        assert results[0].id == species.id

    async def test_get_species_by_ids_empty_list_returns_empty(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_ids with an empty list returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        results = await SpeciesRepository(async_session).get_species_by_ids([])

        assert results == []

    # ============================================================================
    # Get All Species Tests
    # ============================================================================

    async def test_get_all_species_returns_all(
        self, async_session: AsyncSession
    ) -> None:
        """get_all_species returns every species in the catalog.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session)
        await _create_test_species(async_session)
        await _create_test_species(async_session)

        results = await SpeciesRepository(async_session).get_all_species()

        assert len(results) == 3

    async def test_get_all_species_ordered_by_common_name(
        self, async_session: AsyncSession
    ) -> None:
        """get_all_species returns results ordered alphabetically by common_name.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, common_name="Zebra Fish")
        await _create_test_species(async_session, common_name="Angelfish")
        await _create_test_species(async_session, common_name="Moray Eel")

        results = await SpeciesRepository(async_session).get_all_species()

        assert [s.common_name for s in results] == [
            "Angelfish",
            "Moray Eel",
            "Zebra Fish",
        ]

    async def test_get_all_species_limit_restricts_results(
        self, async_session: AsyncSession
    ) -> None:
        """get_all_species respects the limit parameter.

        Args:
            async_session: Database session for the test.
        """
        for i in range(5):
            await _create_test_species(async_session, common_name=f"Fish {i:02d}")

        results = await SpeciesRepository(async_session).get_all_species(limit=3)

        assert len(results) == 3

    async def test_get_all_species_offset_skips_results(
        self, async_session: AsyncSession
    ) -> None:
        """get_all_species respects the offset parameter.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, common_name="Aardvark Fish")
        await _create_test_species(async_session, common_name="Barracuda")
        await _create_test_species(async_session, common_name="Clownfish")

        results = await SpeciesRepository(async_session).get_all_species(offset=1)

        assert len(results) == 2
        assert results[0].common_name == "Barracuda"

    async def test_get_all_species_empty_catalog_returns_empty(
        self, async_session: AsyncSession
    ) -> None:
        """get_all_species returns an empty list when the catalog is empty.

        Args:
            async_session: Database session for the test.
        """
        results = await SpeciesRepository(async_session).get_all_species()

        assert results == []

    # ============================================================================
    # Get By Category Tests
    # ============================================================================

    async def test_get_species_by_category_returns_matching(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_category returns species whose taxonomy contains the category.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(
            async_session,
            common_name="Clownfish",
            taxonomy={"category": "fish", "order": "Perciformes"},
        )
        await _create_test_species(
            async_session,
            common_name="Brain Coral",
            taxonomy={"category": "coral", "order": "Scleractinia"},
        )

        results = await SpeciesRepository(async_session).get_species_by_category("fish")

        assert len(results) == 1
        assert results[0].common_name == "Clownfish"

    async def test_get_species_by_category_excludes_non_matching(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_category excludes species whose taxonomy lacks the category.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(
            async_session,
            taxonomy={"category": "coral"},
        )

        results = await SpeciesRepository(async_session).get_species_by_category("fish")

        assert results == []

    async def test_get_species_by_category_is_case_insensitive(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_category performs a case-insensitive match.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(
            async_session,
            taxonomy={"category": "Fish"},
        )

        results = await SpeciesRepository(async_session).get_species_by_category("fish")

        assert len(results) == 1

    async def test_get_species_by_category_applies_limit(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_category respects the limit parameter.

        Args:
            async_session: Database session for the test.
        """
        for i in range(4):
            await _create_test_species(
                async_session,
                common_name=f"Fish {i:02d}",
                taxonomy={"category": "fish"},
            )

        results = await SpeciesRepository(async_session).get_species_by_category(
            "fish", limit=2
        )

        assert len(results) == 2

    async def test_get_species_by_category_empty_when_none_match(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_category returns an empty list when nothing matches.

        Args:
            async_session: Database session for the test.
        """
        results = await SpeciesRepository(async_session).get_species_by_category(
            "mammal"
        )

        assert results == []

    # ============================================================================
    # Get By ML Label Tests
    # ============================================================================

    async def test_get_species_by_ml_label_returns_correct_species(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_ml_label returns the species with the given label.

        Args:
            async_session: Database session for the test.
        """
        species = await _create_test_species(
            async_session, ml_label="acanthurus_lineatus"
        )

        result = await SpeciesRepository(async_session).get_species_by_ml_label(
            "acanthurus_lineatus"
        )

        assert result is not None
        assert result.id == species.id

    async def test_get_species_by_ml_label_returns_none_when_not_found(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_ml_label returns None for an unknown label.

        Args:
            async_session: Database session for the test.
        """
        result = await SpeciesRepository(async_session).get_species_by_ml_label(
            "nonexistent_label"
        )

        assert result is None

    async def test_get_species_by_ml_label_is_exact_match(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_ml_label does not return partial matches.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, ml_label="acanthurus_lineatus")

        result = await SpeciesRepository(async_session).get_species_by_ml_label(
            "acanthurus"
        )

        assert result is None

    # ============================================================================
    # Get By Slug Tests
    # ============================================================================

    async def test_get_species_by_slug_returns_correct_species(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_slug returns the species with the given slug.

        Args:
            async_session: Database session for the test.
        """
        species = await _create_test_species(async_session, slug="lined-surgeonfish")

        result = await SpeciesRepository(async_session).get_species_by_slug(
            "lined-surgeonfish"
        )

        assert result is not None
        assert result.id == species.id

    async def test_get_species_by_slug_returns_none_when_not_found(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_slug returns None for an unknown slug.

        Args:
            async_session: Database session for the test.
        """
        result = await SpeciesRepository(async_session).get_species_by_slug(
            "nonexistent-slug"
        )

        assert result is None

    async def test_get_species_by_slug_returns_none_when_slug_not_set(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_by_slug does not match species whose slug is None.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session)  # no slug

        result = await SpeciesRepository(async_session).get_species_by_slug("some-slug")

        assert result is None

    # ============================================================================
    # Get Count Tests
    # ============================================================================

    async def test_get_species_count_returns_correct_count(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_count returns the total number of species.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session)
        await _create_test_species(async_session)
        await _create_test_species(async_session)

        count = await SpeciesRepository(async_session).get_species_count()

        assert count == 3

    async def test_get_species_count_returns_zero_when_empty(
        self, async_session: AsyncSession
    ) -> None:
        """get_species_count returns 0 when the catalog is empty.

        Args:
            async_session: Database session for the test.
        """
        count = await SpeciesRepository(async_session).get_species_count()

        assert count == 0

    # ============================================================================
    # Search Species Tests
    # ============================================================================

    async def test_search_species_matches_common_name(
        self, async_session: AsyncSession
    ) -> None:
        """search_species returns species whose common_name contains the query.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, common_name="Clownfish")
        await _create_test_species(async_session, common_name="Blue Tang")

        results = await SpeciesRepository(async_session).search_species("clown")

        assert len(results) == 1
        assert results[0].common_name == "Clownfish"

    async def test_search_species_matches_scientific_name(
        self, async_session: AsyncSession
    ) -> None:
        """search_species returns species whose scientific_name contains the query.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(
            async_session,
            scientific_name="Amphiprioninae ocellaris",
            common_name="Clownfish",
        )
        await _create_test_species(
            async_session,
            scientific_name="Paracanthurus hepatus",
            common_name="Blue Tang",
        )

        results = await SpeciesRepository(async_session).search_species(
            "Amphiprioninae"
        )

        assert len(results) == 1
        assert results[0].common_name == "Clownfish"

    async def test_search_species_matches_ml_label(
        self, async_session: AsyncSession
    ) -> None:
        """search_species returns species whose ml_label contains the query.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, ml_label="amphiprion_ocellaris")
        await _create_test_species(async_session, ml_label="paracanthurus_hepatus")

        results = await SpeciesRepository(async_session).search_species("amphiprion")

        assert len(results) == 1
        assert results[0].ml_label == "amphiprion_ocellaris"

    async def test_search_species_is_case_insensitive(
        self, async_session: AsyncSession
    ) -> None:
        """search_species performs a case-insensitive match.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, common_name="Clownfish")

        results = await SpeciesRepository(async_session).search_species("CLOWN")

        assert len(results) == 1

    async def test_search_species_returns_empty_when_no_match(
        self, async_session: AsyncSession
    ) -> None:
        """search_species returns an empty list when nothing matches.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, common_name="Clownfish")

        results = await SpeciesRepository(async_session).search_species("shark")

        assert results == []

    async def test_search_species_respects_limit(
        self, async_session: AsyncSession
    ) -> None:
        """search_species respects the limit parameter.

        Args:
            async_session: Database session for the test.
        """
        for i in range(4):
            await _create_test_species(async_session, common_name=f"Fish {i:02d}")

        results = await SpeciesRepository(async_session).search_species("Fish", limit=2)

        assert len(results) == 2

    async def test_search_species_ordered_by_common_name(
        self, async_session: AsyncSession
    ) -> None:
        """search_species returns results ordered alphabetically by common_name.

        Args:
            async_session: Database session for the test.
        """
        await _create_test_species(async_session, common_name="Zebra Fish")
        await _create_test_species(async_session, common_name="Angelfish")

        results = await SpeciesRepository(async_session).search_species("fish")

        assert results[0].common_name == "Angelfish"
        assert results[1].common_name == "Zebra Fish"
