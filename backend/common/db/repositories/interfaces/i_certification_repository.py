"""Interface for the user certification repository."""

import uuid
from datetime import date
from typing import Any, Optional, Protocol

from common.db.models.user_models import UserCertification


class IUserCertificationRepository(Protocol):
    """Protocol defining the contract for user certification CRUD operations."""

    async def get_certification_by_id(
        self, certification_id: uuid.UUID
    ) -> Optional[UserCertification]:
        """Retrieve a single certification by its ID.

        Args:
            certification_id: The certification UUID.
        """
        ...

    async def get_user_certifications(self, user_id: uuid.UUID) -> list[UserCertification]:
        """Retrieve all certifications for a user, ordered by issued_date descending.

        Args:
            user_id: The user UUID.
        """
        ...

    async def add_user_certification(
        self, *, user_id: uuid.UUID, certification_name: str, issuer: str,
        issued_date: date, **kwargs: Any,
    ) -> uuid.UUID:
        """Add a new certification for a user and return its ID.

        Args:
            user_id: The owning user's UUID.
            certification_name: Name of the certification.
            issuer: Issuing organisation (e.g. PADI, SSI).
            issued_date: Date the certification was issued.
            **kwargs: Optional fields (expiry_date,
                certification_number, notes, verified).

        Raises:
            sqlalchemy.exc.IntegrityError: If *user_id* does not
                reference an existing user.
        """
        ...

    async def update_user_certification(self, certification_id: uuid.UUID, updates: dict) -> None:
        """Update specific fields of a certification.

        Args:
            certification_id: The certification UUID.
            updates: Field-name → new-value mapping.
        """
        ...

    async def delete_user_certification(self, certification_id: uuid.UUID) -> bool:
        """Delete a certification by its ID.

        Args:
            certification_id: The certification UUID.

        Returns:
            True if deleted, False if not found.
        """
        ...
