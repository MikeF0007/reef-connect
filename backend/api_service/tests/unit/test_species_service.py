"""Unit tests for SpeciesService."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from api_service.app.schemas.species_schemas import SpeciesListResponse
from api_service.app.services.species_service import SpeciesService


def _make_species(common_name: str, scientific_name: str = "Testus species"):
    """Build a minimal mock species ORM object."""
    obj = type("MockSpecies", (), {})()
    obj.id = uuid4()
    obj.ml_label = common_name.lower().replace(" ", "_")
    obj.scientific_name = scientific_name
    obj.common_name = common_name
    obj.slug = common_name.lower().replace(" ", "-")
    obj.description = None
    obj.habitat = None
    obj.locations = None
    obj.taxonomy = None
    obj.image_urls = None
    obj.created_at = datetime.now()
    obj.updated_at = datetime.now()
    return obj


class TestSpeciesService:
    """Unit tests for SpeciesService.list_species."""

    @pytest.fixture
    def mock_repo(self, mocker):
        """Return a mock SpeciesRepository."""
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_repo):
        """Return a SpeciesService wired to the mock repo."""
        return SpeciesService(species_repo=mock_repo)

    async def test_list_species_no_filters_calls_get_all(self, service, mock_repo):
        """When search and category are None, get_all_species is called."""
        species = [_make_species("Clownfish")]
        mock_repo.get_all_species = AsyncMock(return_value=species)
        mock_repo.get_species_count = AsyncMock(return_value=1)

        result = await service.list_species(
            search=None, category=None, limit=20, offset=0
        )

        mock_repo.get_all_species.assert_awaited_once_with(limit=20, offset=0)
        mock_repo.get_species_count.assert_awaited_once()
        assert isinstance(result, SpeciesListResponse)
        assert len(result.items) == 1
        assert result.total == 1

    async def test_list_species_search_calls_search_species(self, service, mock_repo):
        """When search is provided, search_species is called."""
        species = [_make_species("Clownfish")]
        mock_repo.search_species = AsyncMock(return_value=species)
        mock_repo.get_species_count = AsyncMock(return_value=5)

        result = await service.list_species(
            search="clown", category=None, limit=20, offset=0
        )

        mock_repo.search_species.assert_awaited_once_with(
            query="clown", limit=20, offset=0
        )
        assert result.total == 5
        assert result.items[0].common_name == "Clownfish"

    async def test_list_species_category_calls_get_by_category(
        self, service, mock_repo
    ):
        """When category is provided (and search is None), get_species_by_category is called."""
        species = [_make_species("Lionfish"), _make_species("Clownfish")]
        mock_repo.get_species_by_category = AsyncMock(return_value=species)
        mock_repo.get_species_count = AsyncMock(return_value=10)

        result = await service.list_species(
            search=None, category="fish", limit=20, offset=0
        )

        mock_repo.get_species_by_category.assert_awaited_once_with(
            category="fish", limit=20, offset=0
        )
        assert len(result.items) == 2

    async def test_list_species_search_takes_precedence_over_category(
        self, service, mock_repo
    ):
        """When both search and category are provided, search_species is used."""
        species = [_make_species("Clownfish")]
        mock_repo.search_species = AsyncMock(return_value=species)
        mock_repo.get_species_count = AsyncMock(return_value=1)

        await service.list_species(
            search="clown", category="reptile", limit=20, offset=0
        )

        mock_repo.search_species.assert_awaited_once()
        mock_repo.get_species_by_category = AsyncMock()
        mock_repo.get_species_by_category.assert_not_awaited()

    async def test_list_species_pagination_metadata(self, service, mock_repo):
        """Returned SpeciesListResponse includes correct pagination fields."""
        mock_repo.get_all_species = AsyncMock(return_value=[])
        mock_repo.get_species_count = AsyncMock(return_value=42)

        result = await service.list_species(
            search=None, category=None, limit=10, offset=30
        )

        assert result.limit == 10
        assert result.offset == 30
        assert result.total == 42
        assert result.items == []
