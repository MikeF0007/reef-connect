"""FastAPI router for dive log endpoints."""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.database import get_db_session
from common.db.repositories.dive_log_repository import DiveLogRepository

from ..schemas.dive_log_schemas import (
    DiveLogCreate,
    DiveLogDateRangeQuery,
    DiveLogQuery,
    DiveLogResponse,
    DiveLogUpdate,
)
from ..services.dive_log_service import DiveLogService


# Placeholder for authentication - replace with actual auth later
def get_current_user_id() -> UUID:
    """Get current user ID from authentication context.

    Returns:
        UUID: The current authenticated user's ID.
    """
    # TODO: Implement proper authentication
    from uuid import uuid4

    return uuid4()  # Placeholder


def get_dive_log_service(
    session: AsyncSession = Depends(get_db_session),
) -> DiveLogService:
    """Dependency to get DiveLogService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        DiveLogService: An instance of DiveLogService.
    """
    repository = DiveLogRepository(session)
    return DiveLogService(repository)


router = APIRouter(prefix="/api/divelogs", tags=["dive-logs"])


@router.get("", response_model=List[DiveLogResponse])
async def get_dive_logs(
    user_id: Optional[UUID] = Query(
        None, description="User ID to get dive logs for (defaults to current user)"
    ),
    sort_by: Optional[str] = Query(
        "date", pattern="^(date|max_depth|duration|location|experience_rating)$"
    ),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    limit: Optional[int] = Query(20, gt=0, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user_id: UUID = Depends(get_current_user_id),
    service: DiveLogService = Depends(get_dive_log_service),
) -> List[DiveLogResponse]:
    """Get dive logs for a user with optional filtering.

    Args:
        user_id: User ID to get dive logs for (defaults to current user).
        sort_by: Column to sort by.
        order: Sort direction.
        limit: Maximum number of results.
        offset: Number of results to skip.
        current_user_id: Current authenticated user ID.
        service: Dive log service instance.

    Returns:
        List[DiveLogResponse]: List of dive logs.
    """
    target_user_id = user_id if user_id is not None else current_user_id
    query = DiveLogQuery(sort_by=sort_by, order=order, limit=limit, offset=offset)
    return await service.get_user_dive_logs(target_user_id, query)


@router.post("", response_model=DiveLogResponse, status_code=201)
async def create_dive_log(
    data: DiveLogCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: DiveLogService = Depends(get_dive_log_service),
) -> DiveLogResponse:
    """Create a new dive log entry for the current user.

    Args:
        data: The dive log data to create.
        user_id: Current authenticated user ID.
        service: Dive log service instance.

    Returns:
        DiveLogResponse: The created dive log data.
    """
    return await service.create_dive_log(user_id, data)


@router.get("/date-range", response_model=List[DiveLogResponse])
async def get_dive_logs_by_date_range(
    start_date: str,
    end_date: str,
    user_id: Optional[UUID] = Query(
        None, description="User ID to get dive logs for (defaults to current user)"
    ),
    sort_by: Optional[str] = Query(
        "date", pattern="^(date|max_depth|duration|location|experience_rating)$"
    ),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    limit: Optional[int] = Query(20, gt=0, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user_id: UUID = Depends(get_current_user_id),
    service: DiveLogService = Depends(get_dive_log_service),
) -> List[DiveLogResponse]:
    """Get dive logs within a date range for a user.

    Args:
        user_id: User ID to get dive logs for (defaults to current user).
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        sort_by: Column to sort by.
        order: Sort direction.
        limit: Maximum number of results.
        offset: Number of results to skip.
        current_user_id: Current authenticated user ID.
        service: Dive log service instance.

    Returns:
        List[DiveLogResponse]: List of dive logs in the date range.
    """
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
        )

    target_user_id = user_id if user_id is not None else current_user_id
    query = DiveLogDateRangeQuery(
        start_date=start,
        end_date=end,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return await service.get_dive_logs_by_date_range(target_user_id, query)


@router.get("/location/{location}", response_model=List[DiveLogResponse])
async def get_dive_logs_by_location(
    location: str,
    user_id: Optional[UUID] = Query(
        None, description="User ID to get dive logs for (defaults to current user)"
    ),
    sort_by: Optional[str] = Query(
        "date", pattern="^(date|max_depth|duration|location|experience_rating)$"
    ),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    limit: Optional[int] = Query(20, gt=0, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user_id: UUID = Depends(get_current_user_id),
    service: DiveLogService = Depends(get_dive_log_service),
) -> List[DiveLogResponse]:
    """Get dive logs by location (case-insensitive partial match) for a user.

    Args:
        location: Partial or full dive site name.
        user_id: User ID to get dive logs for (defaults to current user).
        sort_by: Column to sort by.
        order: Sort direction.
        limit: Maximum number of results.
        offset: Number of results to skip.
        current_user_id: Current authenticated user ID.
        service: Dive log service instance.

    Returns:
        List[DiveLogResponse]: List of matching dive logs.
    """
    target_user_id = user_id if user_id is not None else current_user_id
    query = DiveLogQuery(sort_by=sort_by, order=order, limit=limit, offset=offset)
    return await service.get_dive_logs_by_location(location, target_user_id, query)


@router.get("/{dive_log_id}", response_model=DiveLogResponse)
async def get_dive_log(
    dive_log_id: UUID,
    service: DiveLogService = Depends(get_dive_log_service),
) -> DiveLogResponse:
    """Get a specific dive log by ID.

    Args:
        dive_log_id: The dive log UUID.
        service: Dive log service instance.

    Returns:
        DiveLogResponse: The dive log data.
    """
    try:
        return await service.get_dive_log(dive_log_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{dive_log_id}", response_model=DiveLogResponse)
async def update_dive_log(
    dive_log_id: UUID,
    data: DiveLogUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: DiveLogService = Depends(get_dive_log_service),
) -> DiveLogResponse:
    """Update a dive log if it belongs to the current user.

    Args:
        dive_log_id: The ID of the dive log to update.
        data: The dive log fields to update.
        user_id: Current authenticated user ID.
        service: Dive log service instance.

    Returns:
        DiveLogResponse: The updated dive log data.
    """
    try:
        return await service.update_dive_log(dive_log_id, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{dive_log_id}")
async def delete_dive_log(
    dive_log_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DiveLogService = Depends(get_dive_log_service),
) -> dict:
    """Delete a dive log if it belongs to the current user.

    Args:
        dive_log_id: The ID of the dive log to delete.
        user_id: Current authenticated user ID.
        service: Dive log service instance.

    Returns:
        dict: Success message.
    """
    try:
        await service.delete_dive_log(dive_log_id, user_id)
        return {"message": "Dive log deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
