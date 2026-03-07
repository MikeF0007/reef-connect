"""Service layer for user certification operations."""

from typing import List
from uuid import UUID

from common.db.repositories.user_certification_repository import (
    UserCertificationRepository,
)

from ..schemas.user_schemas import (
    UserCertificationCreate,
    UserCertificationResponse,
    UserCertificationUpdate,
)


class UserCertificationService:
    """Service for managing user certifications."""

    def __init__(self, repository: UserCertificationRepository) -> None:
        self.repository = repository

    async def get_user_certifications(
        self, user_id: UUID
    ) -> List[UserCertificationResponse]:
        """Get all certifications for a user.

        TODO: Implement privacy-aware filtering:
        - Check user's profile visibility settings
        - Return empty array if profile is private or not visible to current user
        """
        certifications = await self.repository.get_user_certifications(user_id)
        return [
            UserCertificationResponse.model_validate(cert) for cert in certifications
        ]

    async def add_user_certification(
        self, user_id: UUID, data: UserCertificationCreate
    ) -> UserCertificationResponse:
        """Add a new certification for a user."""
        cert_id = await self.repository.add_user_certification(
            user_id=user_id, **data.model_dump()
        )
        certification = await self.repository.get_certification_by_id(cert_id)
        return UserCertificationResponse.model_validate(certification)

    async def update_user_certification(
        self, certification_id: UUID, user_id: UUID, data: UserCertificationUpdate
    ) -> UserCertificationResponse:
        """Update a certification if it belongs to the user."""
        # First check if certification exists and belongs to user
        certification = await self.repository.get_certification_by_id(certification_id)
        if not certification or certification.user_id != user_id:
            raise ValueError("Certification not found or access denied")
        await self.repository.update_user_certification(
            certification_id, data.model_dump(exclude_unset=True)
        )
        updated_cert = await self.repository.get_certification_by_id(certification_id)
        return UserCertificationResponse.model_validate(updated_cert)

    async def delete_user_certification(
        self, certification_id: UUID, user_id: UUID
    ) -> None:
        """Delete a certification if it belongs to the user."""
        certification = await self.repository.get_certification_by_id(certification_id)
        if not certification or certification.user_id != user_id:
            raise ValueError("Certification not found or access denied")
        await self.repository.delete_user_certification(certification_id)
