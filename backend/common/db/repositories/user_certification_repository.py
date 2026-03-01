"""DB-based ICertificationRepository implementation.

Provides async CRUD operations for user certifications.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.user_models import UserCertification
from common.db.repositories.interfaces import IUserCertificationRepository


class UserCertificationRepository(IUserCertificationRepository):
    """Provides async CRUD operations for UserCertification model.

    Attributes:
        session: AsyncSession  -- AsyncSession for database operations. This session is used for
            all method calls, ensuring transaction consistency across operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_certification_by_id(
        self, certification_id: uuid.UUID
    ) -> Optional[UserCertification]:
        """Fetch a single certification by primary key.

        Args:
            certification_id: The certification UUID.

        Returns:
            The UserCertification if found, otherwise ``None``.
        """
        stmt = select(UserCertification).where(
            UserCertification.id == certification_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_certifications(self, user_id: uuid.UUID) -> list[UserCertification]:
        """Fetch all certifications for a user, ordered by issued_date desc.

        Args:
            user_id: The user UUID.

        Returns:
            A list of UserCertification instances (empty if none exist).
        """
        stmt = (
            select(UserCertification)
            .where(UserCertification.user_id == user_id)
            .order_by(UserCertification.issued_date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_user_certification(
        self, *, user_id: uuid.UUID, certification_name: str, issuer: str,
        issued_date: date, **kwargs: object,
    ) -> uuid.UUID:
        """Add a new certification for a user and return its ID.

        Args:
            user_id: ID of the owning user.
            certification_name: Name of the certification.
            issuer: Issuing organisation.
            issued_date: Date the certification was issued.
            **kwargs: Optional fields (expiry_date, certification_number,
                notes, verified).

        Returns:
            The UUID of the newly created certification.

        Raises:
            sqlalchemy.exc.IntegrityError: If *user_id* does not
                reference an existing user.
        """
        cert = UserCertification(
            user_id=user_id,
            certification_name=certification_name,
            issuer=issuer,
            issued_date=issued_date,
            **kwargs,
        )
        self.session.add(cert)
        await self.session.flush()
        return cert.id

    async def update_user_certification(self, certification_id: uuid.UUID, updates: dict) -> None:
        """Update specific fields of a certification.

        Only fields present in *updates* are modified.  Set a value to
        ``None`` to clear a field.

        Args:
            certification_id: The certification UUID.
            updates: Field-name → new-value mapping.
        """
        cert = await self.get_certification_by_id(
            certification_id,
        )
        if cert is None:
            return
        for key, value in updates.items():
            if hasattr(cert, key):
                setattr(cert, key, value)
        self.session.add(cert)
        await self.session.flush()

    async def delete_user_certification(self, certification_id: uuid.UUID) -> bool:
        """Delete a certification by its ID.

        Args:
            certification_id: The certification UUID.

        Returns:
            ``True`` if deleted, ``False`` if the certification was not found.
        """
        cert = await self.get_certification_by_id(
            certification_id,
        )
        if cert is None:
            return False
        await self.session.delete(cert)
        await self.session.flush()
        return True
