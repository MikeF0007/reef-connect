"""Integration tests for dive log API endpoints."""

from datetime import date
from uuid import uuid4

import pytest

from common.db.models.core_models import DiveLog
from common.types.enums import DiveType, ExperienceFeeling, DivePurpose


class TestDiveLogAPI:
    """Integration tests for dive log-related API endpoints."""

    @pytest.fixture
    async def dive_logs(self, async_session, mock_current_user_id):
        """Create test dive logs in the database."""
        logs = []
        for i in range(3):
            log = DiveLog(
                user_id=mock_current_user_id,
                dive_date=date(2023, 6, 15 + i),
                dive_title=f"Test Dive {i+1}",
                dive_site="Test Site",
                duration_minutes=45 + i * 5,
                dive_type=DiveType.REEF,
                dive_purpose=DivePurpose.RECREATIONAL,
                max_depth_ft=60.0 + i * 10,
                experience_rating=4 + (i % 2),  # Alternate 4 and 5
                public_notes=f"Test notes {i+1}",
            )
            async_session.add(log)
            logs.append(log)
        await async_session.commit()
        for log in logs:
            await async_session.refresh(log)
        return logs

    async def test_create_dive_log(self, client):
        """Test POST /api/divelogs."""
        dive_data = {
            "date": "2023-07-01",
            "title": "New Test Dive",
            "site": "Test Reef",
            "duration": 50,
            "dive_purpose": "recreational",
            "max_depth": 75.5,
            "log_visibility": "public",
            "experience_rating": 5,
            "public_notes": "Great dive!",
        }
        response = client.post("/api/divelogs", json=dive_data)

        assert response.status_code == 201
        data = response.json()
        assert data["dive_title"] == "New Test Dive"
        assert data["dive_site"] == "Test Reef"
        assert data["duration_minutes"] == 50
        assert "id" in data

    async def test_get_dive_logs(self, client, dive_logs):
        """Test GET /api/divelogs."""
        response = client.get("/api/divelogs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        titles = [item["dive_title"] for item in data]
        assert "Test Dive 1" in titles
        assert "Test Dive 2" in titles
        assert "Test Dive 3" in titles

    async def test_get_dive_logs_empty(self, client):
        """Test GET /api/divelogs when no dive logs exist."""
        response = client.get("/api/divelogs")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_dive_logs_with_pagination(self, client, dive_logs):
        """Test GET /api/divelogs with pagination."""
        response = client.get("/api/divelogs?limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_dive_logs_by_date_range(self, client, dive_logs):
        """Test GET /api/divelogs/date-range."""
        response = client.get(
            "/api/divelogs/date-range?start_date=2023-06-16&end_date=2023-06-17"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should include dives 2 and 3

    async def test_get_dive_logs_by_date_range_with_user_id(
        self, client, dive_logs, mock_current_user_id
    ):
        """Test GET /api/divelogs/date-range with explicit userId."""
        response = client.get(
            f"/api/divelogs/date-range?user_id={mock_current_user_id}&start_date=2023-06-16&end_date=2023-06-17"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_dive_logs_by_date_range_invalid_date(self, client):
        """Test GET /api/divelogs/date-range with invalid date format."""
        response = client.get(
            "/api/divelogs/date-range?start_date=invalid&end_date=2023-06-17"
        )

        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    async def test_get_dive_logs_by_location(self, client, dive_logs):
        """Test GET /api/divelogs/location/{location}."""
        response = client.get("/api/divelogs/location/Test")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_dive_logs_by_location_with_user_id(
        self, client, dive_logs, mock_current_user_id
    ):
        """Test GET /api/divelogs/location/{location} with explicit user_id."""
        response = client.get(
            f"/api/divelogs/location/Test?user_id={mock_current_user_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_dive_logs_by_date_range_wrong_user(self, client, async_session):
        """Test GET /api/divelogs/date-range with another user's user_id."""
        other_user_id = uuid4()
        log = DiveLog(
            user_id=other_user_id,
            dive_date=date(2023, 6, 16),
            dive_title="Other User Dive",
            dive_site="Other Site",
            duration_minutes=45,
        )
        async_session.add(log)
        await async_session.commit()

        response = client.get(
            f"/api/divelogs/date-range?user_id={other_user_id}&start_date=2023-06-15&end_date=2023-06-17"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Should return the other user's data
        assert data[0]["dive_title"] == "Other User Dive"

    async def test_get_dive_logs_by_location_wrong_user(self, client, async_session):
        """Test GET /api/divelogs/location/{location} with another user's user_id."""
        other_user_id = uuid4()
        log = DiveLog(
            user_id=other_user_id,
            dive_date=date(2023, 6, 16),
            dive_title="Other User Dive",
            dive_site="Other Site",
            duration_minutes=45,
        )
        async_session.add(log)
        await async_session.commit()

        response = client.get(f"/api/divelogs/location/Other?user_id={other_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Should return the other user's data
        assert data[0]["dive_title"] == "Other User Dive"

    async def test_get_dive_log(self, client, dive_logs):
        """Test GET /api/divelogs/{dive_log_id}."""
        dive_log_id = dive_logs[0].id
        response = client.get(f"/api/divelogs/{dive_log_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["dive_title"] == "Test Dive 1"
        assert data["dive_site"] == "Test Site"

    async def test_get_dive_log_not_found(self, client):
        """Test GET /api/divelogs/{dive_log_id} for nonexistent dive log."""
        random_id = uuid4()
        response = client.get(f"/api/divelogs/{random_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_dive_log(self, client, dive_logs):
        """Test PATCH /api/divelogs/{dive_log_id}."""
        dive_log_id = dive_logs[0].id
        update_data = {"title": "Updated Dive Title", "experience_rating": 3}
        response = client.patch(f"/api/divelogs/{dive_log_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["dive_title"] == "Updated Dive Title"
        assert data["experience_rating"] == 3
        assert data["dive_site"] == "Test Site"  # unchanged

    async def test_update_dive_log_not_found(self, client):
        """Test PATCH /api/divelogs/{dive_log_id} for nonexistent dive log."""
        random_id = uuid4()
        update_data = {"title": "Updated"}
        response = client.patch(f"/api/divelogs/{random_id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_dive_log_wrong_user(self, client, async_session):
        """Test PATCH /api/divelogs/{dive_log_id} for another user's dive log."""
        other_user_id = uuid4()
        log = DiveLog(
            user_id=other_user_id,
            dive_date=date(2023, 6, 15),
            dive_title="Other User Dive",
            dive_site="Other Site",
            duration_minutes=45,
        )
        async_session.add(log)
        await async_session.commit()

        update_data = {"title": "Hacked"}
        response = client.patch(f"/api/divelogs/{log.id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_dive_log(self, client, dive_logs):
        """Test DELETE /api/divelogs/{dive_log_id}."""
        dive_log_id = dive_logs[0].id
        response = client.delete(f"/api/divelogs/{dive_log_id}")

        assert response.status_code == 200
        assert response.json() == {"message": "Dive log deleted successfully"}

        # Verify it's gone
        response = client.get(f"/api/divelogs/{dive_log_id}")
        assert response.status_code == 404

    async def test_delete_dive_log_not_found(self, client):
        """Test DELETE /api/divelogs/{dive_log_id} for nonexistent dive log."""
        random_id = uuid4()
        response = client.delete(f"/api/divelogs/{random_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_dive_log_wrong_user(self, client, async_session):
        """Test DELETE /api/divelogs/{dive_log_id} for another user's dive log."""
        other_user_id = uuid4()
        log = DiveLog(
            user_id=other_user_id,
            dive_date=date(2023, 6, 15),
            dive_title="Other User Dive",
            dive_site="Other Site",
            duration_minutes=45,
        )
        async_session.add(log)
        await async_session.commit()

        response = client.delete(f"/api/divelogs/{log.id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
