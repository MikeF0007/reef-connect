"""Integration tests for certification API endpoints."""

from datetime import date
from uuid import uuid4

import pytest
from common.db.models.user_models import UserCertification


class TestCertificationAPI:
    """Integration tests for certification-related API endpoints."""

    @pytest.fixture
    async def test_certifications(self, async_session, mock_current_user_id):
        """Create test certifications in the database."""
        certs = []
        for i in range(2):
            cert = UserCertification(
                id=uuid4(),
                user_id=mock_current_user_id,
                certification_name=f"PADI Level {i + 1}",
                issuer="PADI",
                issued_date=date(2021 + i, 1, 1),
                expiry_date=date(2024 + i, 1, 1),
            )
            async_session.add(cert)
            certs.append(cert)
        await async_session.commit()
        for cert in certs:
            await async_session.refresh(cert)
        return certs

    async def test_get_user_certifications(self, client, test_certifications):
        """Test GET /users/me/certifications."""
        response = client.get("/users/me/certifications")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [item["certification_name"] for item in data]
        assert "PADI Level 1" in names
        assert "PADI Level 2" in names

    async def test_get_user_certifications_empty(self, client):
        """Test GET /users/me/certifications when no certifications exist."""
        response = client.get("/users/me/certifications")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_add_user_certification(self, client):
        """Test POST /users/me/certifications."""
        cert_data = {
            "certification_name": "PADI Open Water",
            "issuer": "PADI",
            "issued_date": "2023-01-01",
            "expiry_date": "2026-01-01",
        }
        response = client.post("/users/me/certifications", json=cert_data)

        assert response.status_code == 201
        data = response.json()
        assert data["certification_name"] == "PADI Open Water"
        assert data["issuer"] == "PADI"
        assert "id" in data

    async def test_update_user_certification(self, client, test_certifications):
        """Test PATCH /users/me/certifications/{certification_id}."""
        cert_id = test_certifications[0].id
        update_data = {"certification_name": "Updated Certification"}
        response = client.patch(f"/users/me/certifications/{cert_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["certification_name"] == "Updated Certification"
        assert data["issuer"] == "PADI"  # unchanged

    async def test_update_certification_not_found(self, client):
        """Test PATCH /users/me/certifications/{certification_id} for nonexistent cert."""
        random_id = uuid4()
        update_data = {"certification_name": "Updated"}
        response = client.patch(f"/users/me/certifications/{random_id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_certification_wrong_user(self, client, async_session):
        """Test PATCH /users/me/certifications/{certification_id} for another user's cert."""
        other_user_id = uuid4()
        cert = UserCertification(
            id=uuid4(),
            user_id=other_user_id,  # Different user
            certification_name="Other User Cert",
            issuer="PADI",
            issued_date=date(2023, 1, 1),
            expiry_date=date(2026, 1, 1),
        )
        async_session.add(cert)
        await async_session.commit()

        update_data = {"certification_name": "Hacked"}
        response = client.patch(f"/users/me/certifications/{cert.id}", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_user_certification(self, client, test_certifications):
        """Test DELETE /users/me/certifications/{certification_id}."""
        cert_id = test_certifications[0].id
        response = client.delete(f"/users/me/certifications/{cert_id}")

        assert response.status_code == 200
        assert response.json() == {"message": "Certification deleted successfully"}

        # Verify it's gone
        response = client.get("/users/me/certifications")
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] != str(cert_id)

    async def test_delete_certification_not_found(self, client):
        """Test DELETE /users/me/certifications/{certification_id} for nonexistent cert."""
        random_id = uuid4()
        response = client.delete(f"/users/me/certifications/{random_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_certification_wrong_user(self, client, async_session):
        """Test DELETE /users/me/certifications/{certification_id} for another user's cert."""
        other_user_id = uuid4()
        cert = UserCertification(
            id=uuid4(),
            user_id=other_user_id,  # Different user
            certification_name="Other User Cert",
            issuer="PADI",
            issued_date=date(2023, 1, 1),
            expiry_date=date(2026, 1, 1),
        )
        async_session.add(cert)
        await async_session.commit()

        response = client.delete(f"/users/me/certifications/{cert.id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_other_user_certifications(self, client, async_session):
        """Test GET /users/{user_id}/certifications for another user."""
        other_user_id = uuid4()
        cert = UserCertification(
            id=uuid4(),
            user_id=other_user_id,
            certification_name="Other User Cert",
            issuer="PADI",
            issued_date=date(2023, 1, 1),
            expiry_date=date(2026, 1, 1),
        )
        async_session.add(cert)
        await async_session.commit()

        response = client.get(f"/users/{other_user_id}/certifications")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["certification_name"] == "Other User Cert"

    async def test_invalid_certification_data(self, client):
        """Test POST /users/me/certifications with invalid data."""
        invalid_data = {
            "certification_name": "",  # Empty name
            "issuer": "PADI",
            "issued_date": "2023-01-01",
            "expiry_date": "2026-01-01",
        }
        response = client.post("/users/me/certifications", json=invalid_data)

        assert response.status_code == 422  # Validation error
