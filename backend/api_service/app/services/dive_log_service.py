"""Service layer for dive log operations."""

from typing import List, Optional
from uuid import UUID

from common.db.repositories.dive_log_repository import DiveLogRepository
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.species_repository import SpeciesRepository

from ..schemas.dive_log_schemas import (
    DiveLogCreate,
    DiveLogDateRangeQuery,
    DiveLogDetailedResponse,
    DiveLogQuery,
    DiveLogResponse,
    DiveLogUpdate,
)
from ..schemas.media_schemas import (
    MediaResponse,
    MediaWithTagsResponse,
    SpeciesResponse,
    SpeciesTagResponse,
    TagWithSpeciesResponse,
)


class DiveLogService:
    """Service for managing dive log entries."""

    def __init__(
        self,
        repository: DiveLogRepository,
        media_repository: Optional[MediaRepository] = None,
        species_repository: Optional[SpeciesRepository] = None,
    ) -> None:
        """Initialize the dive log service.

        Args:
            repository (DiveLogRepository): The repository for dive log operations.
            media_repository (Optional[MediaRepository]): Repository for fetching
                associated media. When provided, the detail endpoint will include
                media with species tags in the response.
            species_repository (Optional[SpeciesRepository]): Repository for
                resolving species data on media tags. Required when
                media_repository is provided.
        """
        self.repository = repository
        self.media_repository = media_repository
        self.species_repository = species_repository

    async def create_dive_log(
        self, user_id: UUID, data: DiveLogCreate
    ) -> DiveLogResponse:
        """Create a new dive log entry.

        TODO: Implement unit conversion based on user preferences:
        - Convert temperatures to Celsius from Fahrenheit if user prefers metric
        - Convert depths to meters from feet if user prefers metric
        - Convert pressures to bar from PSI if user prefers metric

        Args:
            user_id (UUID): The ID of the user creating the dive log.
            data (DiveLogCreate): The data for the new dive log.

        Returns:
            DiveLogResponse: The created dive log response.
        """
        dive_log_id = await self.repository.create_dive_log(
            user_id=user_id, **data.model_dump(by_alias=True)
        )
        dive_log = await self.repository.get_dive_log_by_id(dive_log_id)
        return DiveLogResponse.model_validate(dive_log)

    async def get_dive_log(
        self, dive_log_id: UUID, current_user_id: Optional[UUID] = None
    ) -> DiveLogDetailedResponse:
        """Get a dive log by ID including associated media and species tags.

        TODO: Implement unit conversion based on user preferences:
        - Convert temperatures from Fahrenheit to Celsius if user prefers metric
        - Convert depths from feet to meters if user prefers metric
        - Convert pressures from PSI to bar if user prefers metric

        Args:
            dive_log_id (UUID): The ID of the dive log to retrieve.
            current_user_id (Optional[UUID]): The authenticated user's ID, used
                to populate the ``can_edit`` flag on the response.

        Returns:
            DiveLogDetailedResponse: The dive log with associated media and tags.
        """
        dive_log = await self.repository.get_dive_log_by_id(dive_log_id)
        if not dive_log:
            raise ValueError("Dive log not found")

        media_with_tags: list[MediaWithTagsResponse] = []
        if self.media_repository is not None and self.species_repository is not None:
            media_list = await self.media_repository.get_media_by_dive_log(dive_log_id)
            for media in media_list:
                tags = await self.media_repository.get_species_tags_for_media(media.id)
                species_ids = [t.species_id for t in tags]
                if species_ids:
                    species_list = await self.species_repository.get_species_by_ids(
                        species_ids
                    )
                    species_map = {s.id: s for s in species_list}
                else:
                    species_map = {}
                tag_responses = [
                    TagWithSpeciesResponse(
                        tag=SpeciesTagResponse.model_validate(t),
                        species=SpeciesResponse.model_validate(
                            species_map[t.species_id]
                        ),
                    )
                    for t in tags
                    if t.species_id in species_map
                ]
                media_with_tags.append(
                    MediaWithTagsResponse(
                        media=MediaResponse.model_validate(media),
                        tags=tag_responses,
                    )
                )

        can_edit = current_user_id is not None and dive_log.user_id == current_user_id
        # Validate via DiveLogResponse first to avoid accessing the ORM
        # ``media`` relationship (lazy-load incompatible with async sessions)
        # when Pydantic scans attributes of the DiveLog instance.
        base = DiveLogResponse.model_validate(dive_log)
        return DiveLogDetailedResponse(
            **base.model_dump(by_alias=False),
            media=media_with_tags,
            can_edit=can_edit,
        )

    async def get_dive_logs_by_ids(
        self, dive_log_ids: List[UUID]
    ) -> List[DiveLogResponse]:
        """Get multiple dive logs by IDs.

        TODO: Implement unit conversion based on user preferences for each dive log

        Args:
            dive_log_ids (List[UUID]): The list of dive log IDs to retrieve.

        Returns:
            List[DiveLogResponse]: The list of dive log responses.
        """
        dive_logs = await self.repository.get_dive_logs_by_ids(dive_log_ids)
        return [DiveLogResponse.model_validate(dive_log) for dive_log in dive_logs]

    async def get_user_dive_logs(
        self, user_id: UUID, query: Optional[DiveLogQuery] = None
    ) -> List[DiveLogResponse]:
        """Get dive logs for a user with optional filtering.

        TODO: Implement unit conversion based on user preferences for each dive log

        Args:
            user_id (UUID): The ID of the user whose dive logs to retrieve.
            query (Optional[DiveLogQuery]): The query parameters for filtering and sorting.

        Returns:
            List[DiveLogResponse]: The list of dive log responses.
        """
        if query is None:
            query = DiveLogQuery()
        dive_logs = await self.repository.get_dive_logs_by_user(
            user_id=user_id,
            sort_by=query.sort_by,
            order=query.order,
            limit=query.limit,
            offset=query.offset,
        )
        return [DiveLogResponse.model_validate(dive_log) for dive_log in dive_logs]

    async def get_dive_logs_by_location(
        self, location: str, user_id: UUID, query: Optional[DiveLogQuery] = None
    ) -> List[DiveLogResponse]:
        """Get dive logs by location with optional filtering for a user.

        TODO: Implement unit conversion based on user preferences for each dive log

        Args:
            location (str): The location to filter dive logs by.
            user_id (UUID): The ID of the user whose dive logs to retrieve.
            query (Optional[DiveLogQuery]): The query parameters for filtering and sorting.

        Returns:
            List[DiveLogResponse]: The list of dive log responses.
        """
        if query is None:
            query = DiveLogQuery()
        dive_logs = await self.repository.get_dive_logs_by_location(
            location=location,
            user_id=user_id,
            sort_by=query.sort_by,
            order=query.order,
            limit=query.limit,
            offset=query.offset,
        )
        return [DiveLogResponse.model_validate(dive_log) for dive_log in dive_logs]

    async def get_dive_logs_by_date_range(
        self, user_id: UUID, query: DiveLogDateRangeQuery
    ) -> List[DiveLogResponse]:
        """Get dive logs for a user within a date range.

        TODO: Implement unit conversion based on user preferences for each dive log

        Args:
            user_id (UUID): The ID of the user whose dive logs to retrieve.
            query (DiveLogDateRangeQuery): The query parameters including date range, sorting, and
                pagination.

        Returns:
            List[DiveLogResponse]: The list of dive log responses.
        """
        dive_logs = await self.repository.get_dive_logs_by_date_range(
            user_id=user_id,
            start_date=query.start_date,
            end_date=query.end_date,
            sort_by=query.sort_by,
            order=query.order,
            limit=query.limit,
            offset=query.offset,
        )
        return [DiveLogResponse.model_validate(dive_log) for dive_log in dive_logs]

    async def update_dive_log(
        self, dive_log_id: UUID, user_id: UUID, data: DiveLogUpdate
    ) -> DiveLogResponse:
        """Update a dive log if it belongs to the user.

        TODO: Implement unit conversion based on user preferences:
        - Convert temperatures to Celsius from Fahrenheit if user prefers metric
        - Convert depths to meters from feet if user prefers metric
        - Convert pressures to bar from PSI if user prefers metric

        Args:
            dive_log_id (UUID): The ID of the dive log to update.
            user_id (UUID): The ID of the user attempting the update.
            data (DiveLogUpdate): The fields to update in the dive log.

        Returns:
            DiveLogResponse: The updated dive log response.
        """
        # First check if dive log exists and belongs to user
        dive_log = await self.repository.get_dive_log_by_id(dive_log_id)
        if not dive_log or dive_log.user_id != user_id:
            raise ValueError("Dive log not found or access denied")
        await self.repository.update_dive_log(
            dive_log_id, data.model_dump(exclude_unset=True, by_alias=True)
        )
        updated_dive_log = await self.repository.get_dive_log_by_id(dive_log_id)
        return DiveLogResponse.model_validate(updated_dive_log)

    async def delete_dive_log(self, dive_log_id: UUID, user_id: UUID) -> None:
        """Delete a dive log if it belongs to the user."""
        dive_log = await self.repository.get_dive_log_by_id(dive_log_id)
        if not dive_log or dive_log.user_id != user_id:
            raise ValueError("Dive log not found or access denied")
        await self.repository.delete_dive_log(dive_log_id)
