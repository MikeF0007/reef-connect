"""Integration tests for the ScubaDex API endpoint."""

from datetime import date
from uuid import uuid4

import pytest

from common.db.models.core_models import Media, MediaSpeciesTag, ScubadexEntry, Species
from common.db.models.user_models import User
from common.types.enums import MediaStatus, MediaType, SpeciesTagSource


class TestScubaDexAPI:
    """Integration tests for GET /api/scubadex/{user_id}."""

    @pytest.fixture
    async def user(self, async_session, mock_current_user_id):
        """Insert the test user row."""
        u = User(
            id=mock_current_user_id,
            email="diver@example.com",
            username="diver",
            password_hash="hash",
        )
        async_session.add(u)
        await async_session.commit()
        await async_session.refresh(u)
        return u

    @pytest.fixture
    async def clownfish(self, async_session):
        """Insert a Clownfish species."""
        s = Species(
            ml_label="clownfish_ocellaris",
            scientific_name="Amphiprion ocellaris",
            common_name="Clownfish",
        )
        async_session.add(s)
        await async_session.commit()
        await async_session.refresh(s)
        return s

    @pytest.fixture
    async def lionfish(self, async_session):
        """Insert a Lionfish species."""
        s = Species(
            ml_label="lionfish_pterois",
            scientific_name="Pterois volitans",
            common_name="Lionfish",
        )
        async_session.add(s)
        await async_session.commit()
        await async_session.refresh(s)
        return s

    @pytest.fixture
    async def dex_entry(self, async_session, mock_current_user_id, user, clownfish):
        """Insert a ScubaDex entry for the current user with Clownfish."""
        entry = ScubadexEntry(
            user_id=mock_current_user_id,
            species_id=clownfish.id,
            times_encountered=3,
            date_first_encountered=date(2024, 6, 1),
        )
        async_session.add(entry)
        await async_session.commit()
        await async_session.refresh(entry)
        return entry

    @pytest.fixture
    async def two_dex_entries(
        self, async_session, mock_current_user_id, user, clownfish, lionfish
    ):
        """Insert two ScubaDex entries for the current user."""
        entries = [
            ScubadexEntry(
                user_id=mock_current_user_id,
                species_id=clownfish.id,
                times_encountered=3,
                date_first_encountered=date(2024, 6, 1),
            ),
            ScubadexEntry(
                user_id=mock_current_user_id,
                species_id=lionfish.id,
                times_encountered=1,
                date_first_encountered=date(2024, 8, 15),
            ),
        ]
        for e in entries:
            async_session.add(e)
        await async_session.commit()
        return entries

    @pytest.fixture
    async def media_with_tag(
        self, async_session, mock_current_user_id, user, clownfish
    ):
        """Create a media item tagged with Clownfish for the current user."""
        m = Media(
            user_id=mock_current_user_id,
            storage_key=f"media/{mock_current_user_id}/photo.jpg",
            type=MediaType.IMAGE,
            status=MediaStatus.PROCESSED,
        )
        async_session.add(m)
        await async_session.flush()
        tag = MediaSpeciesTag(
            media_id=m.id,
            species_id=clownfish.id,
            source=SpeciesTagSource.USER,
        )
        async_session.add(tag)
        await async_session.commit()
        await async_session.refresh(m)
        return m

    # ---- Empty dex ----

    async def test_empty_dex(self, client, user, mock_current_user_id):
        """GET /api/scubadex/{user_id} returns empty entries when dex is empty."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["entries"] == []
        assert data["total_discovered"] == 0

    # ---- Basic response shape ----

    async def test_single_entry_response_shape(
        self, client, dex_entry, mock_current_user_id
    ):
        """Response for a single entry contains all required fields."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_discovered"] == 1
        entry = data["entries"][0]
        assert entry["encounter_count"] == 3
        assert entry["first_seen_date"] == "2024-06-01"
        assert entry["species"]["common_name"] == "Clownfish"
        assert "sample_media" not in entry or entry["sample_media"] is None

    async def test_multiple_entries(
        self, client, two_dex_entries, mock_current_user_id
    ):
        """Dex with two entries returns both."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_discovered"] == 2
        assert len(data["entries"]) == 2

    # ---- Statistics ----

    async def test_total_species_reflects_catalog_size(
        self, client, dex_entry, clownfish, mock_current_user_id
    ):
        """total_species equals the full catalog count."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        # Only clownfish exists in catalog at this point
        assert data["total_species"] == 1

    async def test_percent_complete_calculation(
        self, client, two_dex_entries, mock_current_user_id
    ):
        """percent_complete is total_discovered / total_species * 100."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        expected = round(data["total_discovered"] / data["total_species"] * 100, 2)
        assert data["percent_complete"] == expected

    async def test_percent_complete_all_discovered(
        self, client, two_dex_entries, mock_current_user_id
    ):
        """percent_complete is 100.0 when all catalog species are discovered."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        # Both species exist in catalog and both are in the dex
        assert data["percent_complete"] == 100.0

    # ---- include_media ----

    async def test_include_media_false_by_default(
        self, client, dex_entry, media_with_tag, mock_current_user_id
    ):
        """sample_media is None when include_media is not set."""
        response = client.get(f"/api/scubadex/{mock_current_user_id}")

        assert response.status_code == 200
        entry = response.json()["entries"][0]
        assert entry["sample_media"] is None

    async def test_include_media_returns_sample_media(
        self, client, dex_entry, media_with_tag, mock_current_user_id
    ):
        """sample_media is populated when include_media=true."""
        response = client.get(
            f"/api/scubadex/{mock_current_user_id}?include_media=true"
        )

        assert response.status_code == 200
        entry = response.json()["entries"][0]
        assert entry["sample_media"] is not None
        assert len(entry["sample_media"]) == 1
        assert entry["sample_media"][0]["id"] == str(media_with_tag.id)

    async def test_include_media_capped_at_three(
        self, client, async_session, mock_current_user_id, user, clownfish, dex_entry
    ):
        """sample_media contains at most 3 items even when more exist."""
        for i in range(5):
            m = Media(
                user_id=mock_current_user_id,
                storage_key=f"media/{mock_current_user_id}/photo_{i}.jpg",
                type=MediaType.IMAGE,
                status=MediaStatus.PROCESSED,
            )
            async_session.add(m)
            await async_session.flush()
            async_session.add(
                MediaSpeciesTag(
                    media_id=m.id,
                    species_id=clownfish.id,
                    source=SpeciesTagSource.USER,
                )
            )
        await async_session.commit()

        response = client.get(
            f"/api/scubadex/{mock_current_user_id}?include_media=true"
        )

        assert response.status_code == 200
        entry = response.json()["entries"][0]
        assert len(entry["sample_media"]) <= 3

    # ---- Other user ----

    async def test_dex_for_other_user_is_empty(
        self, client, dex_entry, mock_current_user_id
    ):
        """Requesting a different user's dex returns their (empty) results."""
        other_user_id = uuid4()
        response = client.get(f"/api/scubadex/{other_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_discovered"] == 0
        assert data["entries"] == []
