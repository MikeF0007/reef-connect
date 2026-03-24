"""FastAPI router for user profile, settings, and privacy endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.database import get_db_session
from common.db.repositories.user_repository import UserRepository

from ..schemas.user_schemas import (
    PrivacySettingsResponse,
    PrivacySettingsUpdate,
    UserProfileResponse,
    UserProfileUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from ..services.user_service import UserService
from .auth_api import get_current_user_id  # noqa: F401  (re-exported for dependency override)


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    """Dependency to get UserService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        UserService: An instance of UserService.
    """
    repository = UserRepository(session)
    return UserService(repository)


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    """Get current user's profile.

    Args:
        user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        UserProfileResponse: The user's profile data.
    """
    try:
        return await service.get_user_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    """Get a user's public profile with privacy filtering.

    Args:
        user_id: The ID of the user whose profile to retrieve.
        current_user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        UserProfileResponse: The user's profile data (privacy-filtered).
    """
    try:
        # For now, just return the profile - privacy filtering can be added later
        # TODO: Implement privacy-aware filtering based on PrivacySettings
        return await service.get_user_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    """Update current user's profile.

    Args:
        data: The profile fields to update.
        user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        UserProfileResponse: The updated profile data.
    """
    try:
        return await service.update_user_profile(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_my_settings(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserSettingsResponse:
    """Get current user's settings.

    Args:
        user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        UserSettingsResponse: The user's settings data.
    """
    try:
        return await service.get_user_settings(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/me/settings", response_model=UserSettingsResponse)
async def update_my_settings(
    data: UserSettingsUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserSettingsResponse:
    """Update current user's settings.

    Args:
        data: The settings fields to update.
        user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        UserSettingsResponse: The updated settings data.
    """
    try:
        return await service.update_user_settings(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/me/privacy", response_model=PrivacySettingsResponse)
async def get_my_privacy_settings(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> PrivacySettingsResponse:
    """Get current user's privacy settings.

    Args:
        user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        PrivacySettingsResponse: The user's privacy settings data.
    """
    try:
        return await service.get_privacy_settings(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/me/privacy", response_model=PrivacySettingsResponse)
async def update_my_privacy_settings(
    data: PrivacySettingsUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> PrivacySettingsResponse:
    """Update current user's privacy settings.

    Args:
        data: The privacy settings fields to update.
        user_id: Current authenticated user ID.
        service: User service instance.

    Returns:
        PrivacySettingsResponse: The updated privacy settings data.
    """
    try:
        return await service.update_privacy_settings(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
