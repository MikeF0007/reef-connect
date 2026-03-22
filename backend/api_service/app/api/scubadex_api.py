"""FastAPI router for the ScubaDex endpoint."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.database import get_db_session
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.scubadex_repository import ScubaDexRepository
from common.db.repositories.species_repository import SpeciesRepository

from ..schemas.scubadex_schemas import ScubaDexResponse
from ..services.scubadex_service import ScubaDexService


def get_scubadex_service(
    session: AsyncSession = Depends(get_db_session),
) -> ScubaDexService:
    """Dependency to get ScubaDexService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        ScubaDexService: An instance of ScubaDexService.
    """
    media_repo = MediaRepository(session)
    return ScubaDexService(
        scubadex_repo=ScubaDexRepository(session, media_repo),
        species_repo=SpeciesRepository(session),
        media_repo=media_repo,
    )


router = APIRouter(prefix="/api/scubadex", tags=["scubadex"])


@router.get("/{user_id}", response_model=ScubaDexResponse)
async def get_scubadex(
    user_id: uuid.UUID,
    include_media: bool = Query(
        False, description="Include up to 3 sample media per species"
    ),
    service: ScubaDexService = Depends(get_scubadex_service),
) -> ScubaDexResponse:
    """Get a user's ScubaDex — their personal catalogue of discovered species.

    Returns every species the user has encountered (via tagged media), along
    with encounter counts, first-seen dates, catalog completion statistics,
    and optionally up to 3 sample media items per species.

    Args:
        user_id: UUID of the user whose ScubaDex to retrieve.
        include_media: When ``true``, each entry includes sample media.
        service: ScubaDex service instance.

    Returns:
        ScubaDexResponse with entries and discovery statistics.
    """
    return await service.get_user_dex(user_id=user_id, include_media=include_media)
