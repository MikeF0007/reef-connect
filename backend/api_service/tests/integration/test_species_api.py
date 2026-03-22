"""Integration tests for the species catalog API endpoint."""

import pytest

from common.db.models.core_models import Species


class TestSpeciesAPI:
    """Integration tests for GET /api/species."""

    @pytest.fixture
    async def species_catalog(self, async_session):
        """Insert several species into the catalog."""
        entries = [
            Species(
                ml_label="clownfish_ocellaris",
                scientific_name="Amphiprion ocellaris",
                common_name="Clownfish",
                slug="clownfish",
                taxonomy={"category": "fish"},
            ),
            Species(
                ml_label="hawksbill_turtle",
                scientific_name="Eretmochelys imbricata",
                common_name="Hawksbill Sea Turtle",
                slug="hawksbill-turtle",
                taxonomy={"category": "reptile"},
            ),
            Species(
                ml_label="lionfish_pterois",
                scientific_name="Pterois volitans",
                common_name="Lionfish",
                slug="lionfish",
                taxonomy={"category": "fish"},
            ),
        ]
        for s in entries:
            async_session.add(s)
        await async_session.commit()
        for s in entries:
            await async_session.refresh(s)
        return entries

    # ---- GET /api/species — basic list ----

    async def test_list_species_returns_all(self, client, species_catalog):
        """Test GET /api/species returns all species when no filters are applied."""
        response = client.get("/api/species")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_list_species_empty_catalog(self, client):
        """Test GET /api/species returns empty list when catalog is empty."""
        response = client.get("/api/species")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_species_response_shape(self, client, species_catalog):
        """Test GET /api/species response includes expected fields on each item."""
        response = client.get("/api/species")

        assert response.status_code == 200
        item = response.json()["items"][0]
        for field in ("id", "ml_label", "scientific_name", "common_name", "slug"):
            assert field in item

    async def test_list_species_ordered_alphabetically(self, client, species_catalog):
        """Test GET /api/species returns species ordered by common_name."""
        response = client.get("/api/species")

        assert response.status_code == 200
        names = [item["common_name"] for item in response.json()["items"]]
        assert names == sorted(names)

    # ---- Pagination ----

    async def test_list_species_pagination_limit(self, client, species_catalog):
        """Test GET /api/species respects limit parameter."""
        response = client.get("/api/species?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert data["total"] == 3

    async def test_list_species_pagination_offset(self, client, species_catalog):
        """Test GET /api/species respects offset parameter."""
        first_page = client.get("/api/species?limit=2&offset=0").json()["items"]
        second_page = client.get("/api/species?limit=2&offset=2").json()["items"]

        all_ids = {item["id"] for item in first_page} | {
            item["id"] for item in second_page
        }
        assert len(all_ids) == 3

    async def test_list_species_limit_too_high_rejected(self, client, species_catalog):
        """Test GET /api/species rejects limit > 100."""
        response = client.get("/api/species?limit=101")

        assert response.status_code == 422

    async def test_list_species_limit_zero_rejected(self, client, species_catalog):
        """Test GET /api/species rejects limit=0."""
        response = client.get("/api/species?limit=0")

        assert response.status_code == 422

    # ---- Search ----

    async def test_list_species_search_by_common_name(self, client, species_catalog):
        """Test GET /api/species?search matches common name."""
        response = client.get("/api/species?search=clown")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["common_name"] == "Clownfish"

    async def test_list_species_search_by_scientific_name(
        self, client, species_catalog
    ):
        """Test GET /api/species?search matches scientific name."""
        response = client.get("/api/species?search=Pterois")

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["ml_label"] == "lionfish_pterois"

    async def test_list_species_search_by_ml_label(self, client, species_catalog):
        """Test GET /api/species?search matches ml_label."""
        response = client.get("/api/species?search=hawksbill")

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["common_name"] == "Hawksbill Sea Turtle"

    async def test_list_species_search_no_match(self, client, species_catalog):
        """Test GET /api/species?search returns empty list when nothing matches."""
        response = client.get("/api/species?search=shark")

        assert response.status_code == 200
        assert response.json()["items"] == []

    # ---- Category filter ----

    async def test_list_species_category_filter(self, client, species_catalog):
        """Test GET /api/species?category filters by taxonomy category."""
        response = client.get("/api/species?category=fish")

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 2
        common_names = {item["common_name"] for item in items}
        assert common_names == {"Clownfish", "Lionfish"}

    async def test_list_species_category_no_match(self, client, species_catalog):
        """Test GET /api/species?category returns empty list when no match."""
        response = client.get("/api/species?category=mammal")

        assert response.status_code == 200
        assert response.json()["items"] == []

    async def test_list_species_search_takes_precedence_over_category(
        self, client, species_catalog
    ):
        """Test that search takes precedence over category when both are supplied."""
        # "clown" matches only Clownfish; category=reptile would match only turtle
        response = client.get("/api/species?search=clown&category=reptile")

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["common_name"] == "Clownfish"
