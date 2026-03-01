"""DB-based IDiveLogRepository implementation.

Provides async CRUD operations for dive log entries.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.models.core_models import DiveLog
from common.db.repositories.interfaces import IDiveLogRepository


# Maps the public sort_by names from the interface contract to ORM columns.
_SORT_COLUMNS = {
    "date": DiveLog.dive_date,
    "maxDepth": DiveLog.max_depth_ft,
    "duration": DiveLog.duration_minutes,
    "location": DiveLog.dive_site,
    "experienceRating": DiveLog.experience_rating,
}


class DiveLogRepository(IDiveLogRepository):
    """Provides async CRUD operations for DiveLog entries.

    Attributes:
        session: AsyncSession used for all DB operations, ensuring
            transaction consistency across method calls.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ================ Helpers ================

    def _build_order_expr(
        self, sort_by: Optional[str], order: Optional[str], default: str = "date"
    ):
        """Return an SQLAlchemy order expression.

        Args:
            sort_by: Public sort key (see ``_SORT_COLUMNS``). Falls back
                to ``default`` when ``None`` or unrecognised.
            order: ``"asc"`` or ``"desc"``. Defaults to ``"desc"``.
            default: Fallback sort key when *sort_by* is invalid.

        Returns:
            An SQLAlchemy ``asc``/``desc`` expression.
        """
        column = _SORT_COLUMNS.get(sort_by or default, _SORT_COLUMNS[default])
        direction = asc if (order or "desc").lower() == "asc" else desc
        return direction(column)

    def _apply_pagination(self, stmt, limit: Optional[int], offset: Optional[int]):
        """Apply optional OFFSET / LIMIT clauses to a statement.

        Args:
            stmt: The current select statement.
            limit: Maximum number of rows. Skipped when ``None``.
            offset: Number of rows to skip. Skipped when ``None``.

        Returns:
            The modified statement.
        """
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return stmt

    # ================ DiveLog CRUD ================

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
        dive_log = DiveLog(
            user_id=user_id,
            dive_date=dive_date,
            dive_title=dive_title,
            dive_site=dive_site,
            duration_minutes=duration_minutes,
            **kwargs,
        )
        self.session.add(dive_log)
        await self.session.flush()
        return dive_log.id

    async def get_dive_log_by_id(self, dive_log_id: uuid.UUID) -> Optional[DiveLog]:
        """Retrieve a single dive log by its ID.

        Args:
            dive_log_id: The dive log UUID.

        Returns:
            The DiveLog if found, otherwise ``None``.
        """
        stmt = select(DiveLog).where(DiveLog.id == dive_log_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_dive_logs_by_ids(
        self, dive_log_ids: list[uuid.UUID]
    ) -> list[DiveLog]:
        """Retrieve dive logs by their IDs in a single query.

        Args:
            dive_log_ids: UUIDs to look up.

        Returns:
            A list of found DiveLog instances (missing IDs are silently skipped).
        """
        if not dive_log_ids:
            return []
        stmt = select(DiveLog).where(DiveLog.id.in_(dive_log_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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
        order_expr = self._build_order_expr(sort_by, order)
        stmt = select(DiveLog).where(DiveLog.user_id == user_id).order_by(order_expr)
        stmt = self._apply_pagination(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_dive_logs_by_location(
        self,
        location: str,
        *,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[DiveLog]:
        """Retrieve dive logs by dive site (case-insensitive partial match).

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
        order_expr = self._build_order_expr(sort_by, order)
        stmt = (
            select(DiveLog)
            .where(DiveLog.dive_site.ilike(f"%{location}%"))
            .order_by(order_expr)
        )
        stmt = self._apply_pagination(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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
        """Retrieve dive logs for a user within an inclusive date range.

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
        order_expr = self._build_order_expr(sort_by, order)
        stmt = (
            select(DiveLog)
            .where(
                DiveLog.user_id == user_id,
                DiveLog.dive_date >= start_date,
                DiveLog.dive_date <= end_date,
            )
            .order_by(order_expr)
        )
        stmt = self._apply_pagination(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_dive_log(self, dive_log_id: uuid.UUID, updates: dict) -> None:
        """Update specific fields of a dive log.

        Only fields present in *updates* are modified. Set a value to
        ``None`` to clear an optional field.

        Args:
            dive_log_id: The UUID of the dive log to update.
            updates: Field-name → new-value mapping.
        """
        dive_log = await self.get_dive_log_by_id(dive_log_id)
        if dive_log is None:
            return
        for key, value in updates.items():
            if hasattr(dive_log, key):
                setattr(dive_log, key, value)
        self.session.add(dive_log)
        await self.session.flush()

    async def delete_dive_log(self, dive_log_id: uuid.UUID) -> bool:
        """Delete a dive log by its ID.

        Associated media items survive the deletion with their
        ``dive_log_id`` set to ``NULL`` (SET NULL constraint).

        Args:
            dive_log_id: The UUID of the dive log to delete.

        Returns:
            ``True`` if the dive log was deleted, ``False`` if not found.
        """
        dive_log = await self.get_dive_log_by_id(dive_log_id)
        if dive_log is None:
            return False
        await self.session.delete(dive_log)
        await self.session.flush()
        return True
