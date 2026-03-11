"""Integration tests for media and species tagging API endpoints."""

import io
from uuid import uuid4

import pytest

from common.db.models.core_models import DiveLog, Media, MediaSpeciesTag, Species
from common.db.models.user_models import User
from common.types.enums import MediaStatus, MediaType, SpeciesTagSource, Visibility


class TestMediaAPI:
    """Integration tests for media-related API endpoints."""

    @pytest.fixture
    async def user(self, async_session, mock_current_user_id):
        """Insert a minimal User row for the mock current user."""
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
    async def dive_log(self, async_session, mock_current_user_id):
        """Create a test dive log belonging to the current user."""
        from datetime import date

        log = DiveLog(
            user_id=mock_current_user_id,
            dive_date=date(2024, 1, 1),
            dive_title="Test Dive",
            dive_site="Test Reef",
            duration_minutes=45,
        )
        async_session.add(log)
        await async_session.commit()
        await async_session.refresh(log)
        return log

    @pytest.fixture
    async def species(self, async_session):
        """Create a test species for tagging."""
        s = Species(
            ml_label="clownfish_ocellaris",
            scientific_name="Amphiprioninae ocellaris",
            common_name="Clownfish",
        )
        async_session.add(s)
        await async_session.commit()
        await async_session.refresh(s)
        return s

    @pytest.fixture
    async def media_items(self, async_session, mock_current_user_id, dive_log):
        """Create test media items attached to the dive log."""
        items = []
        for i in range(2):
            m = Media(
                user_id=mock_current_user_id,
                storage_key=f"media/{mock_current_user_id}/photo_{i}.jpg",
                type=MediaType.IMAGE,
                status=MediaStatus.PROCESSED,
                dive_log_id=dive_log.id,
                mime_type="image/jpeg",
                description=f"Photo {i + 1}",
            )
            async_session.add(m)
            items.append(m)
        await async_session.commit()
        for m in items:
            await async_session.refresh(m)
        return items

    @pytest.fixture
    async def media_with_tag(self, async_session, media_items, species):
        """Create a species tag on the first media item."""
        tag = MediaSpeciesTag(
            media_id=media_items[0].id,
            species_id=species.id,
            source=SpeciesTagSource.USER,
        )
        async_session.add(tag)
        await async_session.commit()
        return media_items[0], tag

    # ---- GET /api/media ----

    async def test_get_media_by_user(self, client, media_items, mock_current_user_id):
        """Test GET /api/media filtered by user_id."""
        response = client.get(f"/api/media?user_id={mock_current_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("media" in item for item in data)
        assert all("tags" in item for item in data)

    async def test_get_media_by_dive_log(self, client, media_items, dive_log):
        """Test GET /api/media filtered by dive_log_id."""
        response = client.get(f"/api/media?dive_log_id={dive_log.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_media_defaults_to_current_user(self, client, media_items):
        """Test GET /api/media with no filters defaults to current user."""
        response = client.get("/api/media")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_media_empty(self, client):
        """Test GET /api/media returns empty list when user has no media."""
        response = client.get("/api/media")

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_media_with_tags(self, client, media_with_tag, species):
        """Test GET /api/media includes species tags in response."""
        media_item, _ = media_with_tag
        response = client.get(f"/api/media?dive_log_id={media_item.dive_log_id}")

        assert response.status_code == 200
        data = response.json()
        # Find the media item that has a tag
        tagged = next(d for d in data if d["media"]["id"] == str(media_item.id))
        assert len(tagged["tags"]) == 1
        assert tagged["tags"][0]["species"]["common_name"] == "Clownfish"

    async def test_get_media_pagination(
        self, client, media_items, mock_current_user_id
    ):
        """Test GET /api/media pagination."""
        response = client.get(
            f"/api/media?user_id={mock_current_user_id}&limit=1&offset=0"
        )

        assert response.status_code == 200
        assert len(response.json()) == 1

    # ---- POST /api/media/upload ----

    async def test_upload_media_image(self, client, dive_log):
        """Test POST /api/media/upload with a valid image file."""
        file_content = b"fake jpeg data"
        response = client.post(
            "/api/media/upload",
            data={"dive_log_id": str(dive_log.id)},
            files={"file": ("photo.jpg", io.BytesIO(file_content), "image/jpeg")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["upload_status"] == "accepted"
        assert data["media"]["type"] == "image"
        assert data["media"]["mime_type"] == "image/jpeg"

    async def test_upload_media_with_caption(self, client, dive_log):
        """Test POST /api/media/upload stores caption as description."""
        response = client.post(
            "/api/media/upload",
            data={"dive_log_id": str(dive_log.id), "caption": "Beautiful coral"},
            files={"file": ("photo.jpg", io.BytesIO(b"data"), "image/jpeg")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["media"]["description"] == "Beautiful coral"

    async def test_upload_media_video(self, client, dive_log):
        """Test POST /api/media/upload accepts video files."""
        response = client.post(
            "/api/media/upload",
            data={"dive_log_id": str(dive_log.id)},
            files={"file": ("clip.mp4", io.BytesIO(b"video data"), "video/mp4")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["upload_status"] == "accepted"
        assert data["media"]["type"] == "video"

    async def test_upload_media_unsupported_type(self, client, dive_log):
        """Test POST /api/media/upload rejects unsupported MIME types."""
        response = client.post(
            "/api/media/upload",
            data={"dive_log_id": str(dive_log.id)},
            files={"file": ("doc.pdf", io.BytesIO(b"pdf data"), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["upload_status"] == "rejected"

    # ---- PATCH /api/media/:media_id ----

    async def test_update_media_description(self, client, media_items):
        """Test PATCH /api/media/:media_id updates description."""
        media_id = media_items[0].id
        response = client.patch(
            f"/api/media/{media_id}",
            json={"description": "Updated caption"},
        )

        assert response.status_code == 200
        assert response.json()["description"] == "Updated caption"

    async def test_update_media_not_found(self, client):
        """Test PATCH /api/media/:media_id for nonexistent media."""
        response = client.patch(f"/api/media/{uuid4()}", json={"description": "x"})

        assert response.status_code == 404

    async def test_update_media_wrong_user(self, client, async_session):
        """Test PATCH /api/media/:media_id for another user's media."""
        other_user_id = uuid4()
        m = Media(
            user_id=other_user_id,
            storage_key=f"media/{other_user_id}/photo.jpg",
            type=MediaType.IMAGE,
            status=MediaStatus.PENDING,
        )
        async_session.add(m)
        await async_session.commit()

        response = client.patch(f"/api/media/{m.id}", json={"description": "stolen"})

        assert response.status_code == 404

    # ---- DELETE /api/media/:media_id ----

    async def test_delete_media(self, client, media_items):
        """Test DELETE /api/media/:media_id removes the media item."""
        media_id = media_items[0].id
        response = client.delete(f"/api/media/{media_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["removed_tags_count"] == 0

    async def test_delete_media_with_tags(self, client, media_with_tag):
        """Test DELETE /api/media/:media_id reports removed tag count."""
        media_item, _ = media_with_tag
        response = client.delete(f"/api/media/{media_item.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["removed_tags_count"] == 1

    async def test_delete_media_not_found(self, client):
        """Test DELETE /api/media/:media_id for nonexistent media returns 404."""
        response = client.delete(f"/api/media/{uuid4()}")

        assert response.status_code == 404

    async def test_delete_media_wrong_user(self, client, async_session):
        """Test DELETE /api/media/:media_id for another user's media returns 404."""
        other_user_id = uuid4()
        m = Media(
            user_id=other_user_id,
            storage_key=f"media/{other_user_id}/photo.jpg",
            type=MediaType.IMAGE,
            status=MediaStatus.PENDING,
        )
        async_session.add(m)
        await async_session.commit()

        response = client.delete(f"/api/media/{m.id}")

        assert response.status_code == 404

    # ---- POST /api/media/:media_id/tags ----

    async def test_add_tag(self, client, media_items, species):
        """Test POST /api/media/:media_id/tags adds a species tag."""
        media_id = media_items[0].id
        response = client.post(
            f"/api/media/{media_id}/tags",
            json={"species_id": str(species.id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["tag"]["species_id"] == str(species.id)
        assert data["species"]["common_name"] == "Clownfish"
        assert data["tag"]["source"] == "user"

    async def test_add_tag_duplicate(self, client, media_with_tag, species):
        """Test POST /api/media/:media_id/tags returns 409 for duplicate tag."""
        media_item, _ = media_with_tag
        response = client.post(
            f"/api/media/{media_item.id}/tags",
            json={"species_id": str(species.id)},
        )

        assert response.status_code == 409

    async def test_add_tag_species_not_found(self, client, media_items):
        """Test POST /api/media/:media_id/tags returns 404 for unknown species."""
        response = client.post(
            f"/api/media/{media_items[0].id}/tags",
            json={"species_id": str(uuid4())},
        )

        assert response.status_code == 404

    async def test_add_tag_media_not_found(self, client, species):
        """Test POST /api/media/:media_id/tags returns 404 for unknown media."""
        response = client.post(
            f"/api/media/{uuid4()}/tags",
            json={"species_id": str(species.id)},
        )

        assert response.status_code == 404

    async def test_add_tag_wrong_user(self, client, async_session, species):
        """Test POST /api/media/:media_id/tags returns 404 for another user's media."""
        other_user_id = uuid4()
        m = Media(
            user_id=other_user_id,
            storage_key=f"media/{other_user_id}/photo.jpg",
            type=MediaType.IMAGE,
            status=MediaStatus.PENDING,
        )
        async_session.add(m)
        await async_session.commit()

        response = client.post(
            f"/api/media/{m.id}/tags",
            json={"species_id": str(species.id)},
        )

        assert response.status_code == 404

    # ---- DELETE /api/media/:media_id/tags/:tag_id ----

    async def test_delete_tag(self, client, media_with_tag, species):
        """Test DELETE /api/media/:media_id/tags/:tag_id removes the tag."""
        media_item, _ = media_with_tag
        response = client.delete(f"/api/media/{media_item.id}/tags/{species.id}")

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_tag_not_found(self, client, media_items):
        """Test DELETE /api/media/:media_id/tags/:tag_id for nonexistent tag."""
        response = client.delete(f"/api/media/{media_items[0].id}/tags/{uuid4()}")

        assert response.status_code == 200
        assert response.json()["success"] is False

    async def test_delete_tag_media_not_found(self, client):
        """Test DELETE /api/media/:media_id/tags/:tag_id for nonexistent media."""
        response = client.delete(f"/api/media/{uuid4()}/tags/{uuid4()}")

        assert response.status_code == 404

    async def test_delete_tag_wrong_user(self, client, async_session, species):
        """Test DELETE /api/media/:media_id/tags/:tag_id for another user's media."""
        other_user_id = uuid4()
        m = Media(
            user_id=other_user_id,
            storage_key=f"media/{other_user_id}/photo.jpg",
            type=MediaType.IMAGE,
            status=MediaStatus.PENDING,
        )
        async_session.add(m)
        await async_session.commit()

        response = client.delete(f"/api/media/{m.id}/tags/{species.id}")

        assert response.status_code == 404
