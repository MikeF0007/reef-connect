"""Unit tests for ScubaDexService."""

from datetime import date, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from api_service.app.schemas.scubadex_schemas import ScubaDexResponse
from api_service.app.services.scubadex_service import ScubaDexService


def _make_entry(user_id, species_id, count=1, first_date=None):
    """Build a minimal mock ScubadexEntry ORM object."""
    obj = type("MockEntry", (), {})()
    obj.user_id = user_id
    obj.species_id = species_id
    obj.times_encountered = count
    obj.date_first_encountered = first_date or date(2024, 1, 1)
    return obj


def _make_species(species_id, common_name="Clownfish"):
    """Build a minimal mock Species ORM object."""
    obj = type("MockSpecies", (), {})()
    obj.id = species_id
    obj.ml_label = common_name.lower().replace(" ", "_")
    obj.scientific_name = f"Testus {common_name.lower()}"
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


def _make_media(user_id):
    """Build a minimal mock Media ORM object."""
    obj = type("MockMedia", (), {})()
    obj.id = uuid4()
    obj.user_id = user_id
    obj.status = "processed"
    obj.type = "image"
    obj.dive_log_id = None
    obj.mime_type = "image/jpeg"
    obj.file_size_bytes = None
    obj.description = None
    obj.media_visibility = None
    obj.ml_tagging_status = None
    obj.created_at = datetime.now()
    obj.updated_at = datetime.now()
    return obj


class TestScubaDexService:
    """Unit tests for ScubaDexService.get_user_dex."""

    @pytest.fixture
    def mock_scubadex_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def mock_species_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def mock_media_repo(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_scubadex_repo, mock_species_repo, mock_media_repo):
        return ScubaDexService(
            scubadex_repo=mock_scubadex_repo,
            species_repo=mock_species_repo,
            media_repo=mock_media_repo,
        )

    async def test_empty_dex(
        self, service, mock_scubadex_repo, mock_species_repo, mock_media_repo
    ):
        """Empty dex returns zero entries and correct statistics."""
        mock_scubadex_repo.get_user_dex_entries = AsyncMock(return_value=[])
        mock_species_repo.get_species_count = AsyncMock(return_value=10)

        result = await service.get_user_dex(user_id=uuid4(), include_media=False)

        assert isinstance(result, ScubaDexResponse)
        assert result.entries == []
        assert result.total_discovered == 0
        assert result.total_species == 10
        assert result.percent_complete == 0.0

    async def test_single_entry_no_media(
        self, service, mock_scubadex_repo, mock_species_repo, mock_media_repo
    ):
        """Single entry without include_media has sample_media=None."""
        user_id = uuid4()
        species_id = uuid4()
        entry = _make_entry(user_id, species_id, count=5, first_date=date(2024, 3, 10))
        species = _make_species(species_id, "Clownfish")

        mock_scubadex_repo.get_user_dex_entries = AsyncMock(return_value=[entry])
        mock_species_repo.get_species_by_ids = AsyncMock(return_value=[species])
        mock_species_repo.get_species_count = AsyncMock(return_value=1)

        result = await service.get_user_dex(user_id=user_id, include_media=False)

        assert len(result.entries) == 1
        e = result.entries[0]
        assert e.encounter_count == 5
        assert e.first_seen_date == date(2024, 3, 10)
        assert e.species.common_name == "Clownfish"
        assert e.sample_media is None

    async def test_include_media_fetches_per_species(
        self, service, mock_scubadex_repo, mock_species_repo, mock_media_repo
    ):
        """With include_media=True, get_media_by_species_tag is called for each entry."""
        user_id = uuid4()
        species_id = uuid4()
        entry = _make_entry(user_id, species_id)
        species = _make_species(species_id)
        media = _make_media(user_id)

        mock_scubadex_repo.get_user_dex_entries = AsyncMock(return_value=[entry])
        mock_species_repo.get_species_by_ids = AsyncMock(return_value=[species])
        mock_species_repo.get_species_count = AsyncMock(return_value=5)
        mock_media_repo.get_media_by_species_tag = AsyncMock(return_value=[media])

        result = await service.get_user_dex(user_id=user_id, include_media=True)

        mock_media_repo.get_media_by_species_tag.assert_awaited_once_with(
            user_id, species_id, limit=3
        )
        assert result.entries[0].sample_media is not None
        assert len(result.entries[0].sample_media) == 1

    async def test_percent_complete_calculation(
        self, service, mock_scubadex_repo, mock_species_repo, mock_media_repo
    ):
        """percent_complete is correctly calculated."""
        user_id = uuid4()
        s1, s2 = uuid4(), uuid4()
        entries = [_make_entry(user_id, s1), _make_entry(user_id, s2)]
        species = [_make_species(s1, "Fish A"), _make_species(s2, "Fish B")]

        mock_scubadex_repo.get_user_dex_entries = AsyncMock(return_value=entries)
        mock_species_repo.get_species_by_ids = AsyncMock(return_value=species)
        mock_species_repo.get_species_count = AsyncMock(return_value=4)

        result = await service.get_user_dex(user_id=user_id)

        assert result.total_discovered == 2
        assert result.total_species == 4
        assert result.percent_complete == 50.0

    async def test_species_batch_lookup(
        self, service, mock_scubadex_repo, mock_species_repo, mock_media_repo
    ):
        """Species are resolved in a single batch query, not one per entry."""
        user_id = uuid4()
        ids = [uuid4(), uuid4(), uuid4()]
        entries = [_make_entry(user_id, sid) for sid in ids]
        species = [_make_species(sid, f"Species {i}") for i, sid in enumerate(ids)]

        mock_scubadex_repo.get_user_dex_entries = AsyncMock(return_value=entries)
        mock_species_repo.get_species_by_ids = AsyncMock(return_value=species)
        mock_species_repo.get_species_count = AsyncMock(return_value=3)

        await service.get_user_dex(user_id=user_id)

        # get_species_by_ids should be called exactly once with all IDs
        mock_species_repo.get_species_by_ids.assert_awaited_once()
        called_ids = set(mock_species_repo.get_species_by_ids.call_args[0][0])
        assert called_ids == set(ids)

    async def test_zero_catalog_species_gives_zero_percent(
        self, service, mock_scubadex_repo, mock_species_repo, mock_media_repo
    ):
        """percent_complete is 0.0 when catalog is empty to avoid division by zero."""
        mock_scubadex_repo.get_user_dex_entries = AsyncMock(return_value=[])
        mock_species_repo.get_species_count = AsyncMock(return_value=0)

        result = await service.get_user_dex(user_id=uuid4())

        assert result.percent_complete == 0.0
