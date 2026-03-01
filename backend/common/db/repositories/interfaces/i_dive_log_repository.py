"""Interface for the dive log repository."""

import uuid
from datetime import date
from typing import Optional, Protocol

from common.db.models.core_models import DiveLog


class IDiveLogRepository(Protocol):
    """Protocol defining the contract for dive log CRUD operations."""

    async def create_dive_log(
        self,
        *,
        user_id: uuid.UUID,
        dive_date: date,
        dive_title: str,
        dive_site: str,
        duration_minutes: int,
        **kwargs: object,
    ) -> uuid.UUID:
        """Create a new dive log entry and return its ID.

        Args:
            user_id: ID of the owning user.
            dive_date: Date the dive took place.
            dive_title: Title / name for the dive.
            dive_site: Name of the dive site.
            duration_minutes: Total dive duration in minutes.
            **kwargs: Optional model fields
                (max_depth_ft, avg_depth_ft, dive_type, notes, etc.).

        Returns:
            The UUID of the newly created dive log.

        Raises:
            sqlalchemy.exc.IntegrityError: If *user_id* does not
                reference an existing user.
        """
        ...

    async def get_dive_log_by_id(self, dive_log_id: uuid.UUID) -> Optional[DiveLog]:
        """Retrieve a single dive log by its ID.

        Args:
            dive_log_id: The dive log UUID.

        Returns:
            The DiveLog if found, otherwise ``None``.
        """
        ...

    async def get_dive_logs_by_ids(
        self, dive_log_ids: list[uuid.UUID]
    ) -> list[DiveLog]:
        """Retrieve dive logs by their IDs in a single query.

        Args:
            dive_log_ids: List of dive log UUIDs to look up.

        Returns:
            A list of found DiveLog instances (missing IDs are silently skipped).
        """
        ...

    async def get_dive_logs_by_user(
        self,
        user_id: uuid.UUID,
        *,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[DiveLog]:
        """Retrieve dive logs for a user with optional sorting and pagination.

        Args:
            user_id: The user UUID.
            sort_by: Column to sort by. Accepted values: ``"date"``,
                ``"maxDepth"``, ``"duration"``, ``"location"``,
                ``"experienceRating"``. Defaults to ``"date"``.
            order: Sort direction — ``"asc"`` or ``"desc"``.
                Defaults to ``"desc"``.
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            A sorted, paginated list of DiveLog instances.
        """
        ...

    async def get_dive_logs_by_location(
        self,
        location: str,
        *,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[DiveLog]:
        """Retrieve dive logs by dive site location (case-insensitive partial match).

        Args:
            location: Partial or full dive-site name to search for.
            sort_by: Column to sort by. Accepted values: ``"date"``,
                ``"maxDepth"``, ``"duration"``, ``"experienceRating"``.
                Defaults to ``"date"``.
            order: Sort direction — ``"asc"`` or ``"desc"``.
                Defaults to ``"desc"``.
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            A sorted, paginated list of matching DiveLog instances.
        """
        ...

    async def get_dive_logs_by_date_range(
        self,
        user_id: uuid.UUID,
        start_date: date,
        end_date: date,
        *,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[DiveLog]:
        """Retrieve dive logs for a user within a specific date range.

        Args:
            user_id: The user UUID.
            start_date: Inclusive range start date.
            end_date: Inclusive range end date.
            sort_by: Column to sort by. Accepted values: ``"date"``,
                ``"maxDepth"``, ``"duration"``, ``"location"``,
                ``"experienceRating"``. Defaults to ``"date"``.
            order: Sort direction — ``"asc"`` or ``"desc"``.
                Defaults to ``"desc"``.
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            A sorted, paginated list of DiveLog instances within the range.
        """
        ...

    async def update_dive_log(self, dive_log_id: uuid.UUID, updates: dict) -> None:
        """Update specific fields of a dive log.

        Only fields present in *updates* are modified. Set a value to
        ``None`` to clear an optional field.

        Args:
            dive_log_id: The UUID of the dive log to update.
            updates: Field-name → new-value mapping.
        """
        ...

    async def delete_dive_log(self, dive_log_id: uuid.UUID) -> bool:
        """Delete a dive log by its ID.

        Associated media items survive the deletion with their
        ``dive_log_id`` set to ``NULL`` (SET NULL constraint).

        Args:
            dive_log_id: The UUID of the dive log to delete.

        Returns:
            ``True`` if the dive log was deleted, ``False`` if not found.
        """
        ...
