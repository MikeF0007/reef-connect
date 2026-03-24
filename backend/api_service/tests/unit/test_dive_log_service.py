"""Unit tests for DiveLogService."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from api_service.app.schemas.dive_log_schemas import (
    DiveLogCreate,
    DiveLogDateRangeQuery,
    DiveLogQuery,
    DiveLogUpdate,
)
from api_service.app.services.dive_log_service import DiveLogService
from common.types.enums import DivePurpose, ExperienceFeeling, Visibility


class TestDiveLogService:
    """Test cases for DiveLogService methods."""

    @pytest.fixture
    def service(self, mocker):
        """Create a DiveLogService with mocked repository."""
        mock_repo = mocker.Mock()
        return DiveLogService(mock_repo)

    @pytest.fixture
    def user_id(self):
        """Test user ID."""
        return uuid4()

    @pytest.fixture
    def dive_log_id(self):
        """Test dive log ID."""
        return uuid4()

    @pytest.fixture
    def mock_dive_log(self, user_id, dive_log_id):
        """Mock dive log ORM object."""
        mock = type("MockDiveLog", (), {})()
        mock.id = dive_log_id
        mock.user_id = user_id
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        mock.dive_date = date(2023, 6, 15)
        mock.dive_title = "Great Barrier Reef Dive"
        mock.dive_site = "Outer Reef"
        mock.duration_minutes = 45
        mock.dive_type = "reef"  # Use string value instead of enum
        mock.max_depth_ft = 80.5
        mock.experience_rating = 5
        mock.public_notes = "Amazing visibility!"
        return mock

    async def test_create_dive_log(self, service, user_id, mock_dive_log, mocker):
        """Test creating a dive log."""
        data = DiveLogCreate(
            date=date(2023, 6, 15),
            title="Great Barrier Reef Dive",
            site="Outer Reef",
            duration=45,
            purpose=DivePurpose.RECREATIONAL,
            max_depth=80.5,
            log_visibility="public",
            experience_rating=5,
            public_notes="Amazing visibility!",
        )
        service.dive_log_repository.create_dive_log = AsyncMock(return_value=mock_dive_log.id)
        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=mock_dive_log)

        result = await service.create_dive_log(user_id, data)

        service.dive_log_repository.create_dive_log.assert_called_once_with(
            user_id=user_id,
            dive_date=date(2023, 6, 15),
            dive_title="Great Barrier Reef Dive",
            dive_site="Outer Reef",
            duration_minutes=45,
            dive_period=None,
            dive_start_type=None,
            dive_type=None,
            dive_purpose=DivePurpose.RECREATIONAL,
            max_depth_ft=Decimal("80.5"),
            avg_depth_ft=None,
            visibility_ft=None,
            visibility_description=None,
            lat=None,
            long=None,
            log_visibility=Visibility.PUBLIC,
            weather=None,
            air_temp_f=None,
            surface_temp_f=None,
            bottom_temp_f=None,
            water_type=None,
            body_of_water=None,
            wave=None,
            current=None,
            surge=None,
            equipment=None,
            gas_mix=None,
            cylinder_pressure=None,
            safety_stops=None,
            buddy=None,
            dive_center=None,
            experience_feeling=None,
            experience_rating=5,
            public_notes="Amazing visibility!",
            private_notes=None,
        )
        assert result.title == "Great Barrier Reef Dive"

    async def test_get_dive_log_success(
        self, service, dive_log_id, mock_dive_log, mocker
    ):
        """Test getting a dive log successfully."""
        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=mock_dive_log)

        result = await service.get_dive_log(dive_log_id)

        service.dive_log_repository.get_dive_log_by_id.assert_called_once_with(dive_log_id)
        assert result.title == "Great Barrier Reef Dive"

    async def test_get_dive_log_not_found(self, service, dive_log_id, mocker):
        """Test getting a dive log that doesn't exist."""
        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Dive log not found"):
            await service.get_dive_log(dive_log_id)

    async def test_get_dive_logs_by_ids(self, service, mock_dive_log, mocker):
        """Test getting multiple dive logs by IDs."""
        dive_log_ids = [mock_dive_log.id]
        service.dive_log_repository.get_dive_logs_by_ids = AsyncMock(
            return_value=[mock_dive_log]
        )

        result = await service.get_dive_logs_by_ids(dive_log_ids)

        service.dive_log_repository.get_dive_logs_by_ids.assert_called_once_with(dive_log_ids)
        assert len(result) == 1
        assert result[0].title == "Great Barrier Reef Dive"

    async def test_get_user_dive_logs(self, service, user_id, mock_dive_log, mocker):
        """Test getting dive logs for a user."""
        query = DiveLogQuery(sort_by="date", order="desc", limit=10, offset=0)
        service.dive_log_repository.get_dive_logs_by_user = AsyncMock(
            return_value=[mock_dive_log]
        )

        result = await service.get_user_dive_logs(user_id, query)

        service.dive_log_repository.get_dive_logs_by_user.assert_called_once_with(
            user_id=user_id,
            sort_by="date",
            order="desc",
            limit=10,
            offset=0,
        )
        assert len(result) == 1

    async def test_get_user_dive_logs_default_query(
        self, service, user_id, mock_dive_log, mocker
    ):
        """Test getting dive logs with default query parameters."""
        service.dive_log_repository.get_dive_logs_by_user = AsyncMock(
            return_value=[mock_dive_log]
        )

        result = await service.get_user_dive_logs(user_id)

        service.dive_log_repository.get_dive_logs_by_user.assert_called_once_with(
            user_id=user_id,
            sort_by="date",
            order="desc",
            limit=None,
            offset=0,
        )
        assert len(result) == 1

    async def test_get_dive_logs_by_location(
        self, service, user_id, mock_dive_log, mocker
    ):
        """Test getting dive logs by location."""
        location = "reef"
        query = DiveLogQuery(sort_by="date", order="desc")
        service.dive_log_repository.get_dive_logs_by_location = AsyncMock(
            return_value=[mock_dive_log]
        )

        result = await service.get_dive_logs_by_location(location, user_id, query)

        service.dive_log_repository.get_dive_logs_by_location.assert_called_once_with(
            location="reef",
            user_id=user_id,
            sort_by="date",
            order="desc",
            limit=None,
            offset=0,
        )
        assert len(result) == 1

    async def test_get_dive_logs_by_date_range(
        self, service, user_id, mock_dive_log, mocker
    ):
        """Test getting dive logs within a date range."""
        query = DiveLogDateRangeQuery(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            sort_by="date",
            order="desc",
        )
        service.dive_log_repository.get_dive_logs_by_date_range = AsyncMock(
            return_value=[mock_dive_log]
        )

        result = await service.get_dive_logs_by_date_range(user_id, query)

        service.dive_log_repository.get_dive_logs_by_date_range.assert_called_once_with(
            user_id=user_id,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            sort_by="date",
            order="desc",
            limit=None,
            offset=0,
        )
        assert len(result) == 1

    async def test_update_dive_log_success(
        self, service, user_id, dive_log_id, mock_dive_log, mocker
    ):
        """Test updating a dive log successfully."""
        data = DiveLogUpdate(dive_title="Updated Title", experience_rating=4)
        updated_mock = mock_dive_log
        updated_mock.dive_title = "Updated Title"
        updated_mock.experience_rating = 4

        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=mock_dive_log)
        service.dive_log_repository.update_dive_log = AsyncMock(return_value=None)

        result = await service.update_dive_log(dive_log_id, user_id, data)

        service.dive_log_repository.update_dive_log.assert_called_once_with(
            dive_log_id, {"dive_title": "Updated Title", "experience_rating": 4}
        )
        assert result.title == "Updated Title"

    async def test_update_dive_log_not_found(
        self, service, user_id, dive_log_id, mocker
    ):
        """Test updating a dive log that doesn't exist."""
        data = DiveLogUpdate(dive_title="Updated Title")
        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Dive log not found or access denied"):
            await service.update_dive_log(dive_log_id, user_id, data)

    async def test_update_dive_log_wrong_user(
        self, service, user_id, dive_log_id, mock_dive_log, mocker
    ):
        """Test updating a dive log that belongs to another user."""
        data = DiveLogUpdate(dive_title="Updated Title")
        mock_dive_log.user_id = uuid4()  # Different user

        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=mock_dive_log)

        with pytest.raises(ValueError, match="Dive log not found or access denied"):
            await service.update_dive_log(dive_log_id, user_id, data)

    async def test_delete_dive_log_success(
        self, service, user_id, dive_log_id, mock_dive_log, mocker
    ):
        """Test deleting a dive log successfully."""
        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=mock_dive_log)
        service.dive_log_repository.delete_dive_log = AsyncMock(return_value=True)

        await service.delete_dive_log(dive_log_id, user_id)

        service.dive_log_repository.get_dive_log_by_id.assert_called_once_with(dive_log_id)
        service.dive_log_repository.delete_dive_log.assert_called_once_with(dive_log_id)

    async def test_delete_dive_log_not_found(
        self, service, user_id, dive_log_id, mocker
    ):
        """Test deleting a dive log that doesn't exist."""
        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Dive log not found or access denied"):
            await service.delete_dive_log(dive_log_id, user_id)

    async def test_delete_dive_log_wrong_user(
        self, service, user_id, dive_log_id, mock_dive_log, mocker
    ):
        """Test deleting a dive log that belongs to another user."""
        mock_dive_log.user_id = uuid4()  # Different user

        service.dive_log_repository.get_dive_log_by_id = AsyncMock(return_value=mock_dive_log)

        with pytest.raises(ValueError, match="Dive log not found or access denied"):
            await service.delete_dive_log(dive_log_id, user_id)
