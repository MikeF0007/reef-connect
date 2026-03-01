"""Unit tests for DiveLogRepository.

Tests cover all CRUD operations against an in-memory SQLite database.
"""

import uuid
from datetime import date
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.repositories.dive_log_repository import DiveLogRepository
from common.db.repositories.user_repository import UserRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_test_user(session: AsyncSession, **overrides: Any) -> uuid.UUID:
    """Insert a user with sensible defaults and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        overrides: Field values to override the defaults.

    Returns:
        The UUID of the created user.
    """
    defaults = {
        "email": f"{uuid.uuid4().hex[:8]}@example.com",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password_hash": "hashed_pw",
    }
    defaults.update(overrides)
    return await UserRepository(session).create_user(**defaults)


async def _create_test_dive_log(
    session: AsyncSession, user_id: uuid.UUID, **overrides: Any
) -> uuid.UUID:
    """Insert a dive log with sensible defaults and return its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        user_id: Owning user UUID.
        overrides: Field values to override the defaults.

    Returns:
        The UUID of the created dive log.
    """
    defaults = {
        "dive_date": date(2024, 6, 15),
        "dive_title": "Morning Reef Dive",
        "dive_site": "Blue Corner",
        "duration_minutes": 45,
    }
    defaults.update(overrides)
    return await DiveLogRepository(session).create_dive_log(user_id=user_id, **defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDiveLogRepository:
    """Tests for DiveLogRepository covering all CRUD operations."""

    # ============================================================================
    # Create Tests
    # ============================================================================

    async def test_create_dive_log_returns_uuid(
        self, async_session: AsyncSession
    ) -> None:
        """Creating a dive log returns a UUID.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await DiveLogRepository(async_session).create_dive_log(
            user_id=user_id,
            dive_date=date(2024, 6, 15),
            dive_title="Morning Reef Dive",
            dive_site="Blue Corner",
            duration_minutes=45,
        )
        assert isinstance(dive_log_id, uuid.UUID)

    async def test_create_dive_log_persists_required_fields(
        self, async_session: AsyncSession
    ) -> None:
        """All required fields are persisted correctly.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await DiveLogRepository(async_session).create_dive_log(
            user_id=user_id,
            dive_date=date(2024, 6, 15),
            dive_title="Morning Reef Dive",
            dive_site="Blue Corner",
            duration_minutes=45,
        )
        dive_log = await DiveLogRepository(async_session).get_dive_log_by_id(
            dive_log_id
        )
        assert dive_log is not None
        assert dive_log.user_id == user_id
        assert dive_log.dive_date == date(2024, 6, 15)
        assert dive_log.dive_title == "Morning Reef Dive"
        assert dive_log.dive_site == "Blue Corner"
        assert dive_log.duration_minutes == 45

    async def test_create_dive_log_persists_optional_fields(
        self, async_session: AsyncSession
    ) -> None:
        """Optional kwargs are persisted when provided.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await DiveLogRepository(async_session).create_dive_log(
            user_id=user_id,
            dive_date=date(2024, 6, 15),
            dive_title="Deep Dive",
            dive_site="Drop Off",
            duration_minutes=60,
            max_depth_ft=80,
            public_notes="Saw a manta ray!",
        )
        dive_log = await DiveLogRepository(async_session).get_dive_log_by_id(
            dive_log_id
        )
        assert dive_log.max_depth_ft == 80
        assert dive_log.public_notes == "Saw a manta ray!"

    # ============================================================================
    # Lookup Tests
    # ============================================================================

    async def test_get_dive_log_by_id(self, async_session: AsyncSession) -> None:
        """Lookup by ID returns the correct dive log.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await _create_test_dive_log(async_session, user_id)
        fetched = await DiveLogRepository(async_session).get_dive_log_by_id(dive_log_id)
        assert fetched is not None
        assert fetched.id == dive_log_id

    async def test_get_dive_log_by_id_not_found(
        self, async_session: AsyncSession
    ) -> None:
        """Lookup by non-existent ID returns None.

        Args:
            async_session: Database session for the test.
        """
        result = await DiveLogRepository(async_session).get_dive_log_by_id(uuid.uuid4())
        assert result is None

    async def test_get_dive_logs_by_ids(self, async_session: AsyncSession) -> None:
        """Batch lookup returns only existing dive logs.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        id1 = await _create_test_dive_log(async_session, user_id)
        id2 = await _create_test_dive_log(async_session, user_id)
        missing = uuid.uuid4()

        logs = await DiveLogRepository(async_session).get_dive_logs_by_ids(
            [id1, id2, missing]
        )
        found_ids = {log.id for log in logs}
        assert id1 in found_ids
        assert id2 in found_ids
        assert missing not in found_ids

    async def test_get_dive_logs_by_ids_empty_list(
        self, async_session: AsyncSession
    ) -> None:
        """Empty input returns an empty list without hitting the DB.

        Args:
            async_session: Database session for the test.
        """
        logs = await DiveLogRepository(async_session).get_dive_logs_by_ids([])
        assert logs == []

    # ============================================================================
    # Get By User Tests
    # ============================================================================

    async def test_get_dive_logs_by_user_returns_only_that_users_logs(
        self, async_session: AsyncSession
    ) -> None:
        """Only the queried user's dive logs are returned.

        Args:
            async_session: Database session for the test.
        """
        user_a = await _create_test_user(async_session)
        user_b = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_a)
        await _create_test_dive_log(async_session, user_b)

        logs = await DiveLogRepository(async_session).get_dive_logs_by_user(user_a)
        assert len(logs) == 1
        assert logs[0].user_id == user_a

    async def test_get_dive_logs_by_user_default_sort_is_date_desc(
        self, async_session: AsyncSession
    ) -> None:
        """Default sort order is date descending (newest first).

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 1, 1))
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 6, 1))
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 3, 1))

        logs = await DiveLogRepository(async_session).get_dive_logs_by_user(user_id)
        dates = [log.dive_date for log in logs]
        assert dates == sorted(dates, reverse=True)

    async def test_get_dive_logs_by_user_sort_asc(
        self, async_session: AsyncSession
    ) -> None:
        """Ascending sort returns oldest-first results.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 6, 1))
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 1, 1))

        logs = await DiveLogRepository(async_session).get_dive_logs_by_user(
            user_id, sort_by="date", order="asc"
        )
        dates = [log.dive_date for log in logs]
        assert dates == sorted(dates)

    async def test_get_dive_logs_by_user_pagination(
        self, async_session: AsyncSession
    ) -> None:
        """Limit and offset control the result window.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        for i in range(5):
            await _create_test_dive_log(
                async_session, user_id, dive_date=date(2024, 1, i + 1)
            )

        page = await DiveLogRepository(async_session).get_dive_logs_by_user(
            user_id, limit=2, offset=1
        )
        assert len(page) == 2

    async def test_get_dive_logs_by_user_empty(
        self, async_session: AsyncSession
    ) -> None:
        """A user with no dive logs returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        logs = await DiveLogRepository(async_session).get_dive_logs_by_user(user_id)
        assert logs == []

    # ============================================================================
    # Get By Location Tests
    # ============================================================================

    async def test_get_dive_logs_by_location_partial_match(
        self, async_session: AsyncSession
    ) -> None:
        """Partial dive site name matches are returned.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(
            async_session, user_id, dive_site="Blue Corner Wall"
        )
        await _create_test_dive_log(async_session, user_id, dive_site="Blue Hole")
        await _create_test_dive_log(async_session, user_id, dive_site="Palancar Reef")

        logs = await DiveLogRepository(async_session).get_dive_logs_by_location("Blue")
        sites = [log.dive_site for log in logs]
        assert "Blue Corner Wall" in sites
        assert "Blue Hole" in sites
        assert "Palancar Reef" not in sites

    async def test_get_dive_logs_by_location_case_insensitive(
        self, async_session: AsyncSession
    ) -> None:
        """Location search is case-insensitive.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_site="Blue Corner")

        logs = await DiveLogRepository(async_session).get_dive_logs_by_location(
            "blue corner"
        )
        assert len(logs) == 1

    async def test_get_dive_logs_by_location_no_match(
        self, async_session: AsyncSession
    ) -> None:
        """No matches returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_site="Palancar Reef")

        logs = await DiveLogRepository(async_session).get_dive_logs_by_location("zzz")
        assert logs == []

    async def test_get_dive_logs_by_location_pagination(
        self, async_session: AsyncSession
    ) -> None:
        """Limit and offset are applied to location results.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        for i in range(4):
            await _create_test_dive_log(
                async_session, user_id, dive_site=f"Reef Site {i}"
            )

        page = await DiveLogRepository(async_session).get_dive_logs_by_location(
            "Reef Site", limit=2, offset=1
        )
        assert len(page) == 2

    # ============================================================================
    # Get By Date Range Tests
    # ============================================================================

    async def test_get_dive_logs_by_date_range_returns_within_range(
        self, async_session: AsyncSession
    ) -> None:
        """Only dive logs within the date range are returned.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 1, 1))
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 6, 15))
        await _create_test_dive_log(
            async_session, user_id, dive_date=date(2024, 12, 31)
        )

        logs = await DiveLogRepository(async_session).get_dive_logs_by_date_range(
            user_id, date(2024, 3, 1), date(2024, 9, 1)
        )
        assert len(logs) == 1
        assert logs[0].dive_date == date(2024, 6, 15)

    async def test_get_dive_logs_by_date_range_inclusive_boundaries(
        self, async_session: AsyncSession
    ) -> None:
        """The start and end dates are inclusive.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 3, 1))
        await _create_test_dive_log(async_session, user_id, dive_date=date(2024, 9, 1))

        logs = await DiveLogRepository(async_session).get_dive_logs_by_date_range(
            user_id, date(2024, 3, 1), date(2024, 9, 1)
        )
        assert len(logs) == 2

    async def test_get_dive_logs_by_date_range_empty(
        self, async_session: AsyncSession
    ) -> None:
        """No logs in the given range returns an empty list.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_id, dive_date=date(2023, 1, 1))

        logs = await DiveLogRepository(async_session).get_dive_logs_by_date_range(
            user_id, date(2024, 1, 1), date(2024, 12, 31)
        )
        assert logs == []

    async def test_get_dive_logs_by_date_range_only_own_user(
        self, async_session: AsyncSession
    ) -> None:
        """Date range query is scoped to the specified user.

        Args:
            async_session: Database session for the test.
        """
        user_a = await _create_test_user(async_session)
        user_b = await _create_test_user(async_session)
        await _create_test_dive_log(async_session, user_a, dive_date=date(2024, 6, 1))
        await _create_test_dive_log(async_session, user_b, dive_date=date(2024, 6, 1))

        logs = await DiveLogRepository(async_session).get_dive_logs_by_date_range(
            user_a, date(2024, 1, 1), date(2024, 12, 31)
        )
        assert len(logs) == 1
        assert logs[0].user_id == user_a

    # ============================================================================
    # Update Tests
    # ============================================================================

    async def test_update_dive_log_persists_changes(
        self, async_session: AsyncSession
    ) -> None:
        """Updated fields are persisted.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await _create_test_dive_log(async_session, user_id)

        await DiveLogRepository(async_session).update_dive_log(
            dive_log_id,
            {"dive_title": "Renamed Dive", "duration_minutes": 90},
        )
        updated = await DiveLogRepository(async_session).get_dive_log_by_id(dive_log_id)
        assert updated.dive_title == "Renamed Dive"
        assert updated.duration_minutes == 90

    async def test_update_dive_log_clears_optional_field(
        self, async_session: AsyncSession
    ) -> None:
        """Setting an optional field to None clears it.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await DiveLogRepository(async_session).create_dive_log(
            user_id=user_id,
            dive_date=date(2024, 6, 15),
            dive_title="Test",
            dive_site="Site",
            duration_minutes=30,
            public_notes="Some notes",
        )
        await DiveLogRepository(async_session).update_dive_log(
            dive_log_id, {"public_notes": None}
        )
        updated = await DiveLogRepository(async_session).get_dive_log_by_id(dive_log_id)
        assert updated.public_notes is None

    async def test_update_dive_log_not_found_is_noop(
        self, async_session: AsyncSession
    ) -> None:
        """Updating a non-existent dive log is a silent no-op.

        Args:
            async_session: Database session for the test.
        """
        await DiveLogRepository(async_session).update_dive_log(
            uuid.uuid4(), {"dive_title": "Ghost"}
        )
        # No exception raised — silent no-op

    # ============================================================================
    # Delete Tests
    # ============================================================================

    async def test_delete_dive_log_returns_true(
        self, async_session: AsyncSession
    ) -> None:
        """Deleting an existing dive log returns True.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await _create_test_dive_log(async_session, user_id)
        result = await DiveLogRepository(async_session).delete_dive_log(dive_log_id)
        assert result is True

    async def test_delete_dive_log_removes_from_db(
        self, async_session: AsyncSession
    ) -> None:
        """After deletion the dive log is no longer found.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        dive_log_id = await _create_test_dive_log(async_session, user_id)
        await DiveLogRepository(async_session).delete_dive_log(dive_log_id)
        assert (
            await DiveLogRepository(async_session).get_dive_log_by_id(dive_log_id)
            is None
        )

    async def test_delete_dive_log_not_found(self, async_session: AsyncSession) -> None:
        """Deleting a non-existent dive log returns False.

        Args:
            async_session: Database session for the test.
        """
        result = await DiveLogRepository(async_session).delete_dive_log(uuid.uuid4())
        assert result is False
