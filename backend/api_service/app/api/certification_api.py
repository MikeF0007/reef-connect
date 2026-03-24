"""FastAPI router for user certification endpoints."""

from uuid import UUID

from common.db.database import get_db_session
from common.db.repositories.user_certification_repository import (
    UserCertificationRepository,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user_schemas import (
    UserCertificationCreate,
    UserCertificationResponse,
    UserCertificationUpdate,
)
from ..services.user_certification_service import UserCertificationService
from .auth_api import get_current_user_id  # noqa: F401  (re-exported for dependency override)


def get_user_certification_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserCertificationService:
    """Dependency to get UserCertificationService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        UserCertificationService: An instance of UserCertificationService.
    """
    repository = UserCertificationRepository(session)
    return UserCertificationService(repository)


router = APIRouter(prefix="/api/users", tags=["certifications"])


@router.get("/me/certifications", response_model=list[UserCertificationResponse])
async def get_my_certifications(
    user_id: UUID = Depends(get_current_user_id),
    service: UserCertificationService = Depends(get_user_certification_service),
) -> list[UserCertificationResponse]:
    """Get current user's certifications.

    Args:
        user_id: Current authenticated user ID.
        service: User certification service instance.

    Returns:
        list[UserCertificationResponse]: List of user's certifications.
    """
    return await service.get_user_certifications(user_id)


@router.post(
    "/me/certifications", response_model=UserCertificationResponse, status_code=201
)
async def add_my_certification(
    data: UserCertificationCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: UserCertificationService = Depends(get_user_certification_service),
) -> UserCertificationResponse:
    """Add a new certification for current user.

    Args:
        data: The certification data to create.
        user_id: Current authenticated user ID.
        service: User certification service instance.

    Returns:
        UserCertificationResponse: The created certification data.
    """
    return await service.add_user_certification(user_id, data)


@router.patch(
    "/me/certifications/{certification_id}", response_model=UserCertificationResponse
)
async def update_my_certification(
    certification_id: UUID,
    data: UserCertificationUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: UserCertificationService = Depends(get_user_certification_service),
) -> UserCertificationResponse:
    """Update a certification for current user.

    Args:
        certification_id: The ID of the certification to update.
        data: The certification fields to update.
        user_id: Current authenticated user ID.
        service: User certification service instance.

    Returns:
        UserCertificationResponse: The updated certification data.
    """
    try:
        return await service.update_user_certification(certification_id, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/me/certifications/{certification_id}", status_code=204)
async def delete_my_certification(
    certification_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: UserCertificationService = Depends(get_user_certification_service),
) -> None:
    """Delete a certification for current user.

    Args:
        certification_id: The ID of the certification to delete.
        user_id: Current authenticated user ID.
        service: User certification service instance.

    Returns:
        None: 204 No Content on success.
    """
    try:
        await service.delete_user_certification(certification_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{user_id}/certifications", response_model=list[UserCertificationResponse])
async def get_user_certifications(
    user_id: UUID,
    service: UserCertificationService = Depends(get_user_certification_service),
) -> list[UserCertificationResponse]:
    """Get certifications for a specific user (subject to privacy settings).

    Args:
        user_id: The user ID whose certifications to retrieve.
        service: User certification service instance.

    Returns:
        list[UserCertificationResponse]: List of user's certifications.
    """
    try:
        # TODO: Implement privacy filtering based on user's privacy settings
        # For now, return all certifications (this should be filtered based on privacy)
        return await service.get_user_certifications(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
