"""Unit tests for UserCertificationService."""

from datetime import date, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from api_service.app.schemas.user_schemas import UserCertificationCreate, UserCertificationUpdate
from api_service.app.services.user_certification_service import UserCertificationService


class TestUserCertificationService:
    """Test cases for UserCertificationService methods."""

    @pytest.fixture
    def service(self, mocker):
        """Create a UserCertificationService with mocked repository."""
        mock_repo = mocker.Mock()
        return UserCertificationService(mock_repo)

    @pytest.fixture
    def user_id(self):
        """Test user ID."""
        return uuid4()

    @pytest.fixture
    def cert_id(self):
        """Test certification ID."""
        return uuid4()

    @pytest.fixture
    def mock_certification(self, user_id, cert_id):
        """Mock certification ORM object."""
        mock = type("MockCertification", (), {})()
        mock.id = cert_id
        mock.user_id = user_id
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        mock.certification_name = "PADI Open Water"
        mock.issuer = "PADI"
        mock.issued_date = date(2023, 1, 1)
        mock.expiry_date = date(2026, 1, 1)
        mock.certification_number = None
        mock.notes = None
        mock.verified = None
        return mock

    async def test_get_user_certifications(self, service, user_id, mock_certification, mocker):
        """Test getting all certifications for a user."""
        service.repository.get_user_certifications = AsyncMock(return_value=[mock_certification])

        result = await service.get_user_certifications(user_id)

        service.repository.get_user_certifications.assert_called_once_with(user_id)
        assert len(result) == 1
        assert result[0].certification_name == "PADI Open Water"

    async def test_add_user_certification(self, service, user_id, mock_certification, mocker):
        """Test adding a new certification."""
        data = UserCertificationCreate(
            certification_name="PADI Open Water",
            issuer="PADI",
            issued_date="2023-01-01",
            expiry_date="2026-01-01",
        )
        service.repository.add_user_certification = AsyncMock(return_value=uuid4())
        service.repository.get_certification_by_id = AsyncMock(return_value=mock_certification)

        result = await service.add_user_certification(user_id, data)

        service.repository.add_user_certification.assert_called_once_with(
            user_id=user_id,
            certification_name="PADI Open Water",
            issuer="PADI",
            issued_date=date(2023, 1, 1),
            expiry_date=date(2026, 1, 1),
            certification_number=None,
            notes=None,
            verified=None,
        )
        assert result.certification_name == "PADI Open Water"

    async def test_update_user_certification_success(
        self, service, user_id, cert_id, mock_certification, mocker
    ):
        """Test updating a certification successfully."""
        data = UserCertificationUpdate(certification_name="Updated Name")
        updated_mock = mock_certification
        updated_mock.certification_name = "Updated Name"

        service.repository.get_certification_by_id = AsyncMock(return_value=mock_certification)
        service.repository.update_user_certification = AsyncMock(return_value=updated_mock)

        result = await service.update_user_certification(cert_id, user_id, data)

        service.repository.update_user_certification.assert_called_once_with(
            cert_id, {"certification_name": "Updated Name"}
        )
        assert result.certification_name == "Updated Name"

    async def test_update_user_certification_not_found(self, service, user_id, cert_id, mocker):
        """Test updating a certification that doesn't exist."""
        data = UserCertificationUpdate(certification_name="Updated Name")
        service.repository.get_certification_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Certification not found or access denied"):
            await service.update_user_certification(cert_id, user_id, data)

    async def test_update_user_certification_wrong_user(
        self, service, user_id, cert_id, mock_certification, mocker
    ):
        """Test updating a certification that belongs to another user."""
        data = UserCertificationUpdate(certification_name="Updated Name")
        mock_certification.user_id = uuid4()  # Different user

        service.repository.get_certification_by_id = AsyncMock(return_value=mock_certification)

        with pytest.raises(ValueError, match="Certification not found or access denied"):
            await service.update_user_certification(cert_id, user_id, data)

    async def test_delete_user_certification_success(
        self, service, user_id, cert_id, mock_certification, mocker
    ):
        """Test deleting a certification successfully."""
        service.repository.get_certification_by_id = AsyncMock(return_value=mock_certification)
        service.repository.delete_user_certification = AsyncMock()

        await service.delete_user_certification(cert_id, user_id)

        service.repository.get_certification_by_id.assert_called_once_with(cert_id)
        service.repository.delete_user_certification.assert_called_once_with(cert_id)

    async def test_delete_user_certification_not_found(self, service, user_id, cert_id, mocker):
        """Test deleting a certification that doesn't exist."""
        service.repository.get_certification_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Certification not found or access denied"):
            await service.delete_user_certification(cert_id, user_id)

    async def test_delete_user_certification_wrong_user(
        self, service, user_id, cert_id, mock_certification, mocker
    ):
        """Test deleting a certification that belongs to another user."""
        mock_certification.user_id = uuid4()  # Different user

        service.repository.get_certification_by_id = AsyncMock(return_value=mock_certification)

        with pytest.raises(ValueError, match="Certification not found or access denied"):
            await service.delete_user_certification(cert_id, user_id)
        with pytest.raises(ValueError, match="Certification not found or access denied"):
            await service.delete_user_certification(cert_id, user_id)
            await service.delete_user_certification(cert_id, user_id)
