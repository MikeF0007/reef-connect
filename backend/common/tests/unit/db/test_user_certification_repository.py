"""Unit tests for UserCertificationRepository.

Tests cover CRUD operations for UserCertification against an in-memory SQLite database.
"""

import uuid
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.db.repositories.user_certification_repository import (
    UserCertificationRepository,
)
from common.db.repositories.user_repository import UserRepository


async def _create_test_user(session: AsyncSession, **overrides: Any) -> uuid.UUID:
    """Insert a user with sensible defaults, returning its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        overrides: Field values to override the defaults (e.g. email, username).

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


async def _add_test_cert(session: AsyncSession, user_id: uuid.UUID, **overrides: Any) -> uuid.UUID:
    """Insert a certification with sensible defaults, returning its UUID.

    Args:
        session: AsyncSession to use for DB operations.
        user_id: The user ID to associate the certification with.
        overrides: Field values to override the defaults.

    Returns:
        The UUID of the created certification.
    """
    defaults = {
        "user_id": user_id,
        "certification_name": "Open Water Diver",
        "issuer": "PADI",
        "issued_date": date(2024, 1, 15),
    }
    defaults.update(overrides)
    return await UserCertificationRepository(session).add_user_certification(
        **defaults,
    )


class TestUserCertificationRepository:
    """Tests for UserCertificationRepository covering all CRUD operations."""

    # ============================================================================
    # Certification Creation Tests
    # ============================================================================

    async def test_returns_uuid(self, async_session: AsyncSession) -> None:
        """Adding a certification returns a UUID.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await UserCertificationRepository(async_session).add_user_certification(
            user_id=user_id,
            certification_name="Advanced Open Water",
            issuer="PADI",
            issued_date=date(2024, 6, 1),
        )
        assert isinstance(cert_id, uuid.UUID)

    async def test_persists_required_fields(self, async_session: AsyncSession) -> None:
        """Required fields are persisted correctly.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await UserCertificationRepository(async_session).add_user_certification(
            user_id=user_id,
            certification_name="Advanced Open Water",
            issuer="PADI",
            issued_date=date(2024, 6, 1),
        )
        cert = await UserCertificationRepository(async_session).get_certification_by_id(
            cert_id,
        )
        assert cert is not None
        assert cert.user_id == user_id
        assert cert.certification_name == "Advanced Open Water"
        assert cert.issuer == "PADI"
        assert cert.issued_date == date(2024, 6, 1)

    async def test_persists_optional_fields(self, async_session: AsyncSession) -> None:
        """Optional fields (expiry_date, certification_number, notes, verified) persist.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await UserCertificationRepository(async_session).add_user_certification(
            user_id=user_id,
            certification_name="Rescue Diver",
            issuer="SSI",
            issued_date=date(2023, 3, 10),
            expiry_date=date(2025, 3, 10),
            certification_number="SSI-12345",
            notes="Completed in Cozumel",
            verified=True,
        )
        cert = await UserCertificationRepository(async_session).get_certification_by_id(
            cert_id,
        )
        assert cert.expiry_date == date(2025, 3, 10)
        assert cert.certification_number == "SSI-12345"
        assert cert.notes == "Completed in Cozumel"
        assert cert.verified is True

    # ============================================================================
    # Certification Lookup Tests
    # ============================================================================

    async def test_get_by_id(self, async_session: AsyncSession) -> None:
        """Lookup by ID returns the correct certification.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await _add_test_cert(async_session, user_id)
        fetched = await UserCertificationRepository(async_session).get_certification_by_id(
            cert_id,
        )
        assert fetched is not None
        assert fetched.id == cert_id

    async def test_get_by_id_not_found(self, async_session: AsyncSession) -> None:
        """Lookup by non-existent ID returns None.

        Args:
            async_session: Database session for the test.
        """
        result = await UserCertificationRepository(async_session).get_certification_by_id(
            uuid.uuid4(),
        )
        assert result is None

    async def test_get_user_certifications(self, async_session: AsyncSession) -> None:
        """Fetching by user ID returns all certs, ordered by issued_date desc.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        await _add_test_cert(
            async_session,
            user_id,
            certification_name="Open Water",
            issued_date=date(2023, 1, 1),
        )
        await _add_test_cert(
            async_session,
            user_id,
            certification_name="Advanced",
            issued_date=date(2024, 1, 1),
        )
        certs = await UserCertificationRepository(async_session).get_user_certifications(
            user_id,
        )
        assert len(certs) == 2
        assert certs[0].certification_name == "Advanced"
        assert certs[1].certification_name == "Open Water"

    async def test_get_user_certifications_empty(self, async_session: AsyncSession) -> None:
        """Returns an empty list when the user has no certifications.

        Args:
            async_session: Database session for the test.
        """
        certs = await UserCertificationRepository(async_session).get_user_certifications(
            uuid.uuid4(),
        )
        assert certs == []

    # ============================================================================
    # Certification Update Tests
    # ============================================================================

    async def test_update_fields(self, async_session: AsyncSession) -> None:
        """Updating fields via dict persists changes.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await _add_test_cert(async_session, user_id)
        await UserCertificationRepository(async_session).update_user_certification(
            cert_id,
            {
                "certification_name": "Rescue Diver",
                "notes": "Updated notes",
            },
        )
        cert = await UserCertificationRepository(async_session).get_certification_by_id(
            cert_id,
        )
        assert cert.certification_name == "Rescue Diver"
        assert cert.notes == "Updated notes"

    async def test_update_nonexistent_is_noop(self, async_session: AsyncSession) -> None:
        """Updating a non-existent certification is a silent no-op.

        Args:
            async_session: Database session for the test.
        """
        await UserCertificationRepository(async_session).update_user_certification(
            uuid.uuid4(),
            {"certification_name": "Water-Breathing"},
        )
        # No exception raised

    # ============================================================================
    # Certification Deletion Tests
    # ============================================================================

    async def test_delete_returns_true(self, async_session: AsyncSession) -> None:
        """Deleting an existing certification returns True.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await _add_test_cert(async_session, user_id)
        result = await UserCertificationRepository(async_session).delete_user_certification(
            cert_id,
        )
        assert result is True

    async def test_delete_removes_from_db(self, async_session: AsyncSession) -> None:
        """After deletion the certification is no longer found.

        Args:
            async_session: Database session for the test.
        """
        user_id = await _create_test_user(async_session)
        cert_id = await _add_test_cert(async_session, user_id)
        await UserCertificationRepository(async_session).delete_user_certification(
            cert_id,
        )
        assert (
            await UserCertificationRepository(async_session).get_certification_by_id(
                cert_id,
            )
            is None
        )

    async def test_delete_not_found(self, async_session: AsyncSession) -> None:
        """Deleting a non-existent certification returns False.

        Args:
            async_session: Database session for the test.
        """
        result = await UserCertificationRepository(async_session).delete_user_certification(
            uuid.uuid4(),
        )
        assert result is False
