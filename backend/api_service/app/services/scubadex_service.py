"""Service layer for ScubaDex operations."""

import uuid

from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.scubadex_repository import ScubaDexRepository
from common.db.repositories.species_repository import SpeciesRepository

from ..schemas.media_schemas import MediaResponse
from ..schemas.scubadex_schemas import ScubaDexEntryResponse, ScubaDexResponse
from ..schemas.species_schemas import SpeciesCatalogResponse

_SAMPLE_MEDIA_LIMIT = 3


class ScubaDexService:
    """Service for reading a user's ScubaDex (discovered species collection).

    Attributes:
        scubadex_repo: Repository for ScubadexEntry reads.
        species_repo: Repository for resolving species data.
        media_repo: Repository for fetching sample media per species.
    """

    def __init__(
        self,
        scubadex_repo: ScubaDexRepository,
        species_repo: SpeciesRepository,
        media_repo: MediaRepository,
    ) -> None:
        self.scubadex_repo = scubadex_repo
        self.species_repo = species_repo
        self.media_repo = media_repo

    async def get_user_dex(
        self,
        user_id: uuid.UUID,
        include_media: bool = False,
    ) -> ScubaDexResponse:
        """Return the full ScubaDex for a user.

        Fetches all ScubadexEntry rows for the user, resolves the associated
        species in a single batch query, and optionally fetches up to
        ``_SAMPLE_MEDIA_LIMIT`` sample media items per species.

        Args:
            user_id: The UUID of the user whose ScubaDex to retrieve.
            include_media: When ``True``, up to 3 sample media items are
                included for each discovered species.

        Returns:
            ScubaDexResponse with entries, discovery totals, and completion %.
        """
        entries = await self.scubadex_repo.get_user_dex_entries(user_id)

        species_ids = [e.species_id for e in entries]
        if species_ids:
            species_list = await self.species_repo.get_species_by_ids(species_ids)
            species_map = {s.id: s for s in species_list}
        else:
            species_map = {}

        total_species = await self.species_repo.get_species_count()

        entry_responses: list[ScubaDexEntryResponse] = []
        for entry in entries:
            species = species_map.get(entry.species_id)
            if species is None:
                continue

            sample_media = None
            if include_media:
                media_items = await self.media_repo.get_media_by_species_tag(
                    user_id, entry.species_id, limit=_SAMPLE_MEDIA_LIMIT
                )
                sample_media = [MediaResponse.model_validate(m) for m in media_items]

            entry_responses.append(
                ScubaDexEntryResponse(
                    species=SpeciesCatalogResponse.model_validate(species),
                    first_seen_date=entry.date_first_encountered,
                    encounter_count=entry.times_encountered,
                    sample_media=sample_media,
                )
            )

        total_discovered = len(entry_responses)
        percent_complete = (
            round(total_discovered / total_species * 100, 2)
            if total_species > 0
            else 0.0
        )

        return ScubaDexResponse(
            entries=entry_responses,
            total_discovered=total_discovered,
            total_species=total_species,
            percent_complete=percent_complete,
        )
